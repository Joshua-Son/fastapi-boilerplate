from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.encoders import jsonable_encoder

from app import schemas, crud
from app.api.deps import get_db

import uuid

router = APIRouter()

@router.get("", response_model=schemas.ResponseBase)
async def read_arena(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    try:
        arenas = await crud.arena.get_all_arena(db, skip=skip, limit=limit)
        if not arenas:
            # Return a custom message if no arenas are found
            return schemas.ErrorResponse(code=404, message="No participation found", data=None)
        return schemas.SuccessResponse(data=jsonable_encoder(arenas))
    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}", data=None)


@router.post("/create-test", response_model=schemas.ResponseBase)
async def create_arena(db: AsyncSession = Depends(get_db)):
    try:
        uuid_str = str(uuid.uuid4())
        data = {
            "game_id": uuid_str,
            "max_users": 4,
            "entry_fee": 2
        }
        arena_schema = schemas.ArenaCreate(**data)
        res = await crud.arena.create_arena(db, arena_schema)
        return schemas.SuccessResponse(data=jsonable_encoder(res))
    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}", data=None)