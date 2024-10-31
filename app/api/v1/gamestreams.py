from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.encoders import jsonable_encoder

import os
import redis

from app import schemas, crud
from app.api.deps import get_db

router = APIRouter()

# Initialize Redis
cache = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0)

# TODO: vmStart, vmStatus, release, resetSimple, get list, vmReset, researve

# GET
@router.get("", response_model=List[schemas.GameStreamResponse])
async def read_gstreams(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    return await crud.gamestream.get_multi(db, skip=skip, limit=limit)

@router.get("/check_all_caches", response_model=schemas.ResponseBase)
async def check_all_caches():
    # Get all room keys from Redis
    room_keys = cache.keys("room:*:occupied")
    response = {
        "rooms": {}
    }

    for key in room_keys:
        room_id = key.decode("utf-8").split(":")[1]  # Extract room ID from key
    
        is_occupied = cache.get(f"room:{room_id}:occupied")
        room_user_id = cache.get(f"room:{room_id}:user_id")
    
        response["rooms"][room_id] = {
            "is_occupied": bool(is_occupied),
            "user_id": int(room_user_id) if room_user_id else None,
        }

    return schemas.SuccessResponse(data=response)


# POST
@router.post("", response_model=schemas.GameStreamResponse)
async def create_gstream(*, db: AsyncSession = Depends(get_db), gstream_body: schemas.GameStreamCreate):
    gstream = await crud.gamestream.upsert_gamestream(db, gstream_body)
    return gstream

@router.post("/researve", response_model=schemas.ResponseBase)
async def gstream_researve(*, db: AsyncSession = Depends(get_db), gstream_body: schemas.GameStreamReserve):

    try:
        # Check Redis cache for user occupancy
        current_room_id = cache.get(f"user:{gstream_body.player_id}:room_id")
        if current_room_id:
            return schemas.ErrorResponse(code=404, message=f"User is already checked into: {int(current_room_id)}")
        
        # Also check the database for user occupancy
        room = await crud.gamestream.get_by_user_id(db, gstream_body.player_id)
        if room:
            return schemas.ErrorResponse(code=404, message=f"User is already checked into: {room.id}")
        

        gstream = await crud.gamestream.get_idle_stream(db)
        if gstream:
            gstream_update = {"id": gstream.id, "status": "researved", "game_id":gstream_body.game_id, "player_id": gstream_body.player_id}
            gstream = await crud.gamestream.update(db, db_obj=gstream, obj_in=gstream_update)
            # Update Redis cache
            cache.set(f"room:{gstream.id}:occupied", True)
            cache.set(f"room:{gstream.id}:user_id", gstream.player_id)  # Store user ID in cache
            cache.set(f"user:{gstream.player_id}:room_id", gstream.id)  # Cache the room ID for the user
            
            return schemas.SuccessResponse(data=jsonable_encoder(gstream))

        key = gstream_body.nation
        if key == None:
            key = 'kr'
      

    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}")




# # Updated check-in endpoint
# @app.post("/checkin/{user_id}", response_model=dict)
# async def check_in(user_id: int):
#     db = SessionLocal()

#     # Check Redis cache for user occupancy
#     current_room_id = cache.get(f"user:{user_id}:room_id")
    
#     # Also check the database for user occupancy
#     if current_room_id:
#         return {"detail": "User is already checked into a room", "room_id": int(current_room_id)}
    
#     room = db.query(RoomModel).filter(RoomModel.user_id == user_id).first()
#     if room:
#         # User is already checked into a room in the database
#         return {"detail": "User is already checked into a room", "room_id": room.id}

#     # Find a random empty room
#     available_room = db.query(RoomModel).filter(RoomModel.is_occupied == False).first()
#     if not available_room:
#         raise HTTPException(status_code=400, detail="No available rooms")

#     # Mark room as occupied and associate it with the user
#     available_room.is_occupied = True
#     available_room.user_id = user_id
#     db.commit()
    
#     # Update Redis cache
#     cache.set(f"room:{available_room.id}:occupied", True)
#     cache.set(f"room:{available_room.id}:user_id", user_id)  # Store user ID in cache
#     cache.set(f"user:{user_id}:room_id", available_room.id)  # Cache the room ID for the user
    
#     return {"detail": "User checked into room", "room_id": available_room.id}


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



# # Endpoint to check out of a room
# @app.post("/checkout/{user_id}", response_model=dict)
# async def check_out(user_id: int):
#     db = SessionLocal()
#     current_room_id = cache.get(f"user:{user_id}:room_id")

#     if not current_room_id:
#         raise HTTPException(status_code=400, detail="User is not checked into any room")

#     # Find the room associated with the user
#     room = db.query(RoomModel).filter(RoomModel.id == int(current_room_id)).first()
    
#     if not room:
#         raise HTTPException(status_code=404, detail="Room not found")
    
#     # Mark room as available and remove user association
#     room.is_occupied = False
#     room.user_id = None
#     db.commit()
    
#     # Remove from Redis cache
#     cache.delete(f"room:{room.id}:occupied")
#     cache.delete(f"room:{room.id}:user_id")  # Remove user ID from cache
#     cache.delete(f"user:{user_id}:room_id")  # Remove user ID from cache
    
#     return {"detail": "User checked out successfully", "room_id": room.id}

# # To run the app: uvicorn main:app --reload