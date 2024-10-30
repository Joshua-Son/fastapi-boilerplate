from typing import Optional, List, Union, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.participation import Participation
from app.schemas.participation import ParticipationCreate, ParticipationUpdate

from sqlalchemy.future import select

class CRUDParticipation(CRUDBase[Participation, ParticipationCreate, ParticipationUpdate]):
    async def create_participation(self, db: AsyncSession, input: ParticipationCreate) -> Participation:
        return await self.create(db, obj_in=input)

    async def get_participation(self, db: AsyncSession, participation_id: int) -> Optional[Participation]:
        return await self.get(db, model_id=participation_id)

    async def get_all_participations(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Participation]:
        return await self.get_multi(db, skip=skip, limit=limit)

    async def update_participation(self, db: AsyncSession, participation_id: int, input: ParticipationUpdate) -> Optional[Participation]:
        participation = await self.get(db, model_id=participation_id)
        if participation:
            return await self.update(db, db_obj=participation, obj_in=input)
        return None

    async def delete_participation(self, db: AsyncSession, participation_id: int) -> Optional[Participation]:
        return await self.remove(db, model_id=participation_id)
    
    async def get_count(self, db: AsyncSession, *, arena_uuid: str) -> int:
        result = await db.execute(select(self.model).filter(self.model.arena_uuid == arena_uuid))
        return result.scalar() or 0


participation = CRUDParticipation(Participation)
