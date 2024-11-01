from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.encoders import jsonable_encoder

from app import schemas, crud
from app.api.deps import get_db

from typing import Dict

router = APIRouter()

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
            arena_list = await crud.arena.get_empty_arena(db,game_id=arena_body.game_id,entry_fee=int(arena_body.entryFee),limit=arena_body.user_limit)
            print(arena_list)
            return schemas.SuccessResponse(message="TODO Test", data=jsonable_encoder(arena_list))

        if arena is None:
            if create_data is None:
                create_data = {
                    "game_id": arena_body.game_id,
                    "max_users": arena_body.user_limit,
                    "entry_fee": int(arena_body.entryFee)
                }
            
            arena_schema = schemas.ArenaCreate(**create_data)
            arena = await crud.arena.create_arena(db, arena_schema)

            # return schemas.SuccessResponse(data=jsonable_encoder(res))
        else:
            return schemas.SuccessResponse(message="TODO Test")

        encoded_arena = jsonable_encoder(arena)

        participate = {
            "arena_id": encoded_arena.get('id'),
            "user_uuid": arena_body.user_id,
            "challenge": 1
        }

        
        arenaplayer_schema = schemas.ParticipationCreate(**participate)
        arenaplayer = await crud.participation.create_participation(db, arenaplayer_schema)

        return schemas.SuccessResponse(data=arena.id)

    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}", data=None)
    

@router.delete("/all", response_model=schemas.Message)
async def delete_all_data(db: AsyncSession = Depends(get_db)):
    await crud.arena.delete_all_arenas(db)
    return {"message": "Arena all deleted."}