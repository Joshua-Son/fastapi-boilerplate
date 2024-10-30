from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.encoders import jsonable_encoder

from app import schemas, crud
from app.api.deps import get_db

router = APIRouter()

@router.get("", response_model=schemas.ResponseBase)
async def read_participation(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    try:
        participation = await crud.participation.get_all_participations(db, skip=skip, limit=limit)
        
        if not participation:
            return schemas.ErrorResponse(code=404, message="No participation found", data=None)
        return schemas.SuccessResponse(data=jsonable_encoder(participation))
    except Exception as e:
        return schemas.ErrorResponse(code=500, message=f"An error occurred: {str(e)}", data=None)