from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from fastapi.encoders import jsonable_encoder

from app import schemas, crud
from app.api.deps import get_db

from typing import Dict
import json

router = APIRouter()

from app.api.v1.gamestreams import cache 

# TODO: signal, findtournament, removeplaym, removeplayt(torn)

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
        print('Broadcasting:', message)
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
    
@router.get("/signal", response_model=schemas.Message)
async def get_signal(db: AsyncSession = Depends(get_db), arena_id: str = "", player_id: str = "", status: str = "", score: str = "", stream_id: str = "" ):
    try:
        current_room_id = cache.get(f"user:{player_id}:room_id")
        
        if status in ["resultg", "scoreg"] and current_room_id is None:
            return schemas.ErrorResponse(
                code=404,
                message="The gamestream with this User does not exist in the system, or Player Error.",
                data=None
            )

        if status == "resultg":
            offscreen = "offs"
            message_payload = {
                "arena_id": arena_id,
                "status": offscreen,
                "player_id": player_id,
                "score": score
            }
            await Simple.send_msg(player_id, json.dumps(message_payload))

            gstream = await crud.gamestream.get(db, model_id=int(stream_id.strip()))
            if not gstream or gstream.player_id != player_id:
                return schemas.ErrorResponse(
                    code=400,
                    message=f"The gamestream with ID: {stream_id} does not exist or player ID: {player_id} error."
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
            # TODO: await reset_webapi(f"http://{addrapi}/forcereset")

        if status == "scoreg":
            print("call score web api")
            # TODO: result_m_score_webapi(arena_id, player_id, score)

        message_payload = {
            "arena_id": arena_id,
            "status": status,
            "player_id": player_id,
            "score": score
        }
        await Simple.send_msg(player_id, json.dumps(message_payload))

        return {"message": f"GameStream Signal {arena_id} - {player_id} - {status} - {score}."}

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

        return schemas.SuccessResponse(data=arena.id)

    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}", data=None)
    

@router.delete("/all", response_model=schemas.Message)
async def delete_all_data(db: AsyncSession = Depends(get_db)):
    await crud.arena.delete_all_arenas(db)
    return {"message": "Arena all deleted."}