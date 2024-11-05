from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from fastapi.encoders import jsonable_encoder

from app import schemas, crud
from app.api.deps import get_db

from typing import Dict
import json
import httpx


router = APIRouter()

from app.api.v1.gamestreams import cache 

# TODO: findtournament, removeplaym, removeplayt(torn)

vm_forcereset = "/forcereset"

versusnow_url = "http://10.1.80.4"
versusnow_api = "/api/gameApi/arena/upsertHistory/"

class Simple:
    active_connections: Dict[str, WebSocket] = {}

    @staticmethod
    async def send_msg(user_id:str, message: str):
        """Send a message to a specific user."""
        if user_id in Simple.active_connections:
            websocket = Simple.active_connections[user_id]
            await websocket.send_text(message)


    @staticmethod
    async def sm_broadcast(message: str):
        """Broadcast a message to all connected users."""
        rmsocks = []  # List of sockets to remove

        for user_id, ws in Simple.active_connections.items():
            try:
                await ws.send_text(message)
            except Exception as e:
                print('Exception occurred for user:', user_id, e)
                rmsocks.append(user_id)  # Mark user ID for removal

        # Remove disconnected users from active_connections
        for user_id in rmsocks:
            del Simple.active_connections[user_id]

        return message
    
async def request_vm_post(*, vm_api_url: str, vm_ip:str, post_data:Dict[str, Any] = None):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://" + vm_ip + vm_api_url, json=post_data)

        # 200: GET, 201: POST
        if response.status_code == 201:
            try:
                # Parse the JSON response into the SuccessResponseModel
                success_response = schemas.SuccessResponse(**response.json())
                return success_response  # Return the parsed response
            except Exception as e:
                return schemas.ErrorResponse(code=500, message="Error parsing response from external API", data=None)
        else:
            return schemas.ErrorResponse(code=500, message="Failed to call VM Api", data=None)
        
async def request_web_post(*, web_api_url: str, post_data:Dict[str, Any] = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(versusnow_url + web_api_url, json=post_data)

        # 200: GET, 201: POST
        if response.status_code == 201:
            try:
                # Parse the JSON response into the SuccessResponseModel
                success_response = schemas.SuccessResponse(**response.json())
                return success_response  # Return the parsed response
            except Exception as e:
                return schemas.ErrorResponse(code=500, message="Error parsing response from external API", data=None)
        else:
            return schemas.ErrorResponse(code=500, message="Failed to call VM Api", data=None)


@router.get("", response_model=schemas.ResponseBase)
async def read_arena(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    try:
        arenas = await crud.arena.get_all_arena(db, skip=skip, limit=limit)
        if not arenas:
            # Return a custom message if no arenas are found
            return schemas.ErrorResponse(code=404, message="No arena found", data=None)
        return schemas.SuccessResponse(data=jsonable_encoder(arenas))
    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}", data=None)
    
@router.post("/signal", response_model=schemas.Message)
async def post_signal(*, db: AsyncSession = Depends(get_db), signal_body: schemas.SignalAPI ):
    try:
        current_room_id = cache.get(f"user:{signal_body.player_id}:room_id")
        
        if signal_body.status in ["resultg", "scoreg"] and current_room_id is None:
            return schemas.ErrorResponse(
                code=404,
                message="The gamestream with this User does not exist in the system, or Player Error.",
                data=None
            )

        if signal_body.status == "resultg":
            message_payload = {
                "arena_id": signal_body.arena_id,
                "status": "offs",
                "player_id": signal_body.player_id,
                "score": signal_body.score
            }
            await Simple.send_msg(signal_body.player_id, json.dumps(message_payload))

            gstream = await crud.gamestream.get(db, model_id=int(signal_body.stream_id.strip()))
            if not gstream or gstream.player_id != signal_body.player_id:
                return schemas.ErrorResponse(
                    code=400,
                    message=f"The gamestream with ID: {signal_body.stream_id} does not exist or player ID: {signal_body.player_id} error."
                )

            gstream_update = {
                "id": gstream.id,
                "status": "idle",
                "game_id": None,
                "player_id": None,
                "ended": func.now()
            }
            await crud.gamestream.update(db, db_obj=gstream, obj_in=gstream_update)

            # Clean up Redis cache
            cache.set(f"room:{gstream.id}:occupied", "False")
            cache.delete(f"room:{gstream.id}:user_id")
            cache.delete(f"user:{gstream.player_id}:room_id")

            print("call end vm api")
            vm_response = await request_vm_post(vm_api_url=vm_forcereset, vm_ip=gstream.addrapi)

            if isinstance(vm_response, schemas.SuccessResponse):
                print(vm_response.message)
            elif isinstance(vm_response, schemas.ErrorResponse):
                print("error!!!")
                print(vm_response.message)

        if signal_body.status == "scoreg":
            print("call score web api")
            jsondata = {
                "history_id": signal_body.arena_id,
                "user_id": signal_body.player_id,
                "score": signal_body.score
            }
            web_response = await request_web_post(web_api_url=versusnow_api, post_data=jsondata)
            print(web_response.message)


        message_payload = {
            "arena_id": signal_body.arena_id,
            "status": signal_body.status,
            "player_id": signal_body.player_id,
            "score": signal_body.score
        }
        await Simple.send_msg(signal_body.player_id, json.dumps(message_payload))

        return {"message": f"GameStream Signal {signal_body.arena_id} - {signal_body.player_id} - {signal_body.status} - {signal_body.score}."}

    except Exception as e:
        return schemas.ErrorResponse(
            code=500,
            message=f"An error occurred: {str(e)}",
            data=None
        )
   
@router.post("/findmulti", response_model=schemas.ResponseBase)
async def arena_findmulti(*, db: AsyncSession = Depends(get_db), arena_body: schemas.ArenaMultiCreateAPI):
    try:
        arena = None
        create_data = None
        if arena_body.is_practice:
            create_data = {
                "game_id": arena_body.game_id,
                "max_users": 1,
                "entry_fee": None
            }
        else:
            arena_list = await crud.arena.get_empty_arena(db,game_id=arena_body.game_id,entry_fee=int(arena_body.entryFee),user_limit=arena_body.user_limit,user_id=arena_body.user_id)
            print(arena_list)

            if len(arena_list) > 0:
                arena = arena_list[0] if arena_list else None

        if arena is None:
            if create_data is None:
                create_data = {
                    "game_id": arena_body.game_id,
                    "max_users": arena_body.user_limit,
                    "entry_fee": int(arena_body.entryFee)
                }
            
            arena_schema = schemas.ArenaCreate(**create_data)
            arena = await crud.arena.create_arena(db, arena_schema)

        encoded_arena = jsonable_encoder(arena)

        participate = {
            "arena_id": encoded_arena.get('id'),
            "user_uuid": arena_body.user_id,
            "challenge": 1
        }
        
        arenaplayer_schema = schemas.ParticipationCreate(**participate)
        arenaplayer = await crud.participation.create(db, obj_in = arenaplayer_schema)

        print("participation: ")
        print(jsonable_encoder(arenaplayer))

        return schemas.SuccessResponse(code=201, data=arena.id)

    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}", data=None)
    

@router.delete("/all", response_model=schemas.Message)
async def delete_all_data(db: AsyncSession = Depends(get_db)):
    await crud.arena.delete_all_arenas(db)
    return {"message": "Arena all deleted."}