from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.arena import Arena
from app.schemas import ArenaCreate, ArenaUpdate
import datetime

from sqlalchemy.future import select

class CRUDArena(CRUDBase[Arena, ArenaCreate, ArenaUpdate]):
    async def create_arena(self, db: AsyncSession, input: ArenaCreate) -> Arena:
        return await self.create(db, obj_in=input)

    async def get_arena(self, db: AsyncSession, arena_id: int) -> Optional[Arena]:
        return await self.get(db, model_id=arena_id)

    async def get_all_arena(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Arena]:
        return await self.get_multi(db, skip=skip, limit=limit)

    async def update_arena(self, db: AsyncSession, arena_id: int, input: ArenaUpdate) -> Optional[Arena]:
        arena = await self.get(db, model_id=arena_id)
        if arena:
            return await self.update(db, db_obj=arena, obj_in=input)
        return None

    async def delete_arena(self, db: AsyncSession, arena_id: int) -> Optional[Arena]:
        return await self.remove(db, model_id=arena_id)
    
    async def get_empty_arena(self, db: AsyncSession, *, game_id: str, entry_fee: int, limit: int) -> List[Arena]:
        today = datetime.datetime.now()
        delta = datetime.timedelta(minutes=1439)
        ago = today - delta

        result = await db.execute(
            select(self.model)
            .filter(
                self.model.game_id == game_id,
                self.model.current_users < limit,
                self.model.max_users.isnot(None),
                self.model.created_at >= ago
            )
            .order_by(self.model.created_at.asc())
        )
        return result.scalars().all()

arena = CRUDArena(Arena)