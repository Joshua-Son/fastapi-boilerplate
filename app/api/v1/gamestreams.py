from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from fastapi.encoders import jsonable_encoder

import os
import redis

cache = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0)

from app import schemas, crud
from app.api.deps import get_db

router = APIRouter()



# TODO: vmStart, vmStatus, get list, vmReset

async def reset_redis(db: AsyncSession):
    gstrems_db = await crud.gamestream.get_gstream_all(db)
    for gstream in gstrems_db:
        if (gstream.status != "idle"):
            cache.set(f"room:{gstream.id}:occupied", "True")
            cache.set(f"room:{gstream.id}:user_id", gstream.player_id)  # Store user ID in cache
            cache.set(f"user:{gstream.player_id}:room_id", gstream.id)  # Cache the room ID for the user
        else:
            cache.set(f"room:{gstream.id}:occupied", "False")

async def check_redis(db: AsyncSession):
    room_keys = cache.keys("room:*:occupied")

    if len(room_keys) == 0:
        await reset_redis(db)
        room_keys = cache.keys("room:*:occupied")

    return room_keys            


# GET
@router.get("", response_model=List[schemas.GameStreamResponse])
async def read_gstreams(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    return await crud.gamestream.get_multi(db, skip=skip, limit=limit)

@router.get("/checkSimple", response_model=schemas.ResponseBase)
async def check_all_caches(db: AsyncSession = Depends(get_db)):
    room_keys = await check_redis(db)
    response = {
        "rooms": {}
    }

    for key in room_keys:
        room_id = key.decode("utf-8").split(":")[1]  # Extract room ID from key
    
        is_occupied = cache.get(f"room:{room_id}:occupied")
        room_user_id = cache.get(f"room:{room_id}:user_id")
        
        is_occupied = is_occupied.decode("utf-8") == "True"
   
        response["rooms"][room_id] = {
            "is_occupied": is_occupied,
            "user_id": room_user_id if room_user_id else None,
        }
    
    return schemas.SuccessResponse(data=response)



# POST
@router.post("", response_model=schemas.GameStreamResponse)
async def create_gstream(*, db: AsyncSession = Depends(get_db), gstream_body: schemas.GameStreamCreate):
    gstream = await crud.gamestream.upsert_gstream(db, gstream_body)
    return gstream

@router.post("/resetSimple", response_model=schemas.Message)
async def reset_redis_manually(db: AsyncSession = Depends(get_db)):
    try:
        await reset_redis(db)
        return {"message": "Redis reset done."}
    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}")


@router.post("/researve", response_model=schemas.ResponseBase)
async def gstream_researve(*, db: AsyncSession = Depends(get_db), gstream_body: schemas.GameStreamReserve):
    try:
        room_keys = await check_redis(db)

        if len(room_keys) > 0:
            # Check Redis cache for user occupancy
            current_room_id = cache.get(f"user:{gstream_body.player_id}:room_id")
            if current_room_id:
                return schemas.ErrorResponse(code=404, message=f"User is already checked into: {int(current_room_id)}")
            
            # Check which rooms are occupied
            unoccupied_rooms = [
                key.decode("utf-8").split(":")[1] 
                for key in room_keys 
                    if cache.get(key).decode("utf-8") == "False"  # Check for unoccupied rooms
            ]
            
            if len(unoccupied_rooms) > 0:
                gstream = await crud.gamestream.get(db, model_id=int(unoccupied_rooms[0]))
                if gstream == None:
                    return schemas.ErrorResponse(code=404, message="Redis Database got wrong")

                gstream_update = {"id": gstream.id, "status": "researved", "game_id":gstream_body.game_id, "player_id": gstream_body.player_id, "started":func.now(), "ended":None}
                updated_gstream = await crud.gamestream.update(db, db_obj=gstream, obj_in=gstream_update)

                cache.set(f"room:{updated_gstream.id}:occupied", "True")
                cache.set(f"room:{updated_gstream.id}:user_id", updated_gstream.player_id)  # Store user ID in cache
                cache.set(f"user:{updated_gstream.player_id}:room_id", updated_gstream.id)  # Cache the room ID for the user
                   
                return schemas.SuccessResponse(data=jsonable_encoder(updated_gstream))

            # key = gstream_body.nation
            # if key == None:
            #     key = 'kr'

        return schemas.ErrorResponse(code=404, message="The available Game Stream Server does not exist. Try again later")
  
    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}")
    

@router.post("/release", response_model=schemas.ResponseBase)
async def gstream_release(*, db: AsyncSession = Depends(get_db), gstream_body: schemas.GameStreamReleaseQuit):
    try:
        gstream = await crud.gamestream.get(db, model_id=gstream_body.id)

        if not gstream or gstream.player_id != gstream_body.player_id:
            return schemas.ErrorResponse(code=400, message=f"The gamestream with ID: {gstream_body.id} does not exist in the system or player id: {gstream_body.player_id} error")
        
        gstream_update = {"id": gstream.id, "status": "idle", "game_id":None, "player_id": None, "ended":func.now()}
        gstream = await crud.gamestream.update(db, db_obj=gstream, obj_in=gstream_update)

        # Remove from Redis cache
        cache.set(f"room:{gstream.id}:occupied", "False")
        cache.delete(f"room:{gstream.id}:user_id")  # Remove user ID from cache
        cache.delete(f"user:{gstream.player_id}:room_id")  # Remove user ID from cache

        return schemas.SuccessResponse(data=jsonable_encoder(gstream))

    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}")


# PUT
@router.put("", response_model=schemas.GameStreamResponse)
async def update_gstream(*, db: AsyncSession = Depends(get_db), gstream_body: schemas.GameStreamUpdate):
    try:
        gstream = await crud.gamestream.get(db, model_id=gstream_body.id)

        if not gstream:
            return schemas.ErrorResponse(code=404, message="The gstream with this ID does not exist in the system.")
        
        gstream = await crud.gamestream.update(db, db_obj=gstream, obj_in=gstream_body)
        return gstream

    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}")

    
# DELETE
@router.delete("", response_model=schemas.Message)
async def delete_gstream(*, db: AsyncSession = Depends(get_db), id: int):
    try:
        gstream = await crud.gamestream.get(db, model_id=id)
        if not gstream:
            return schemas.ErrorResponse(code=404, message="The gstream with this ID does not exist in the system.")
        
        await crud.gamestream.remove(db, model_id=gstream.id)
        cache.delete(f"room:{gstream.id}:occupied")
        cache.delete(f"room:{gstream.id}:user_id")
        
        return {"message": f"GameStream with ID = {id} deleted."}   

    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}")
