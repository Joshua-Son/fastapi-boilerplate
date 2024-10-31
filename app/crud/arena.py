from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.crud.base import CRUDBase
from app.models.arena import Arena
from app.schemas.arena import ArenaCreate, ArenaUpdate
import datetime

from sqlalchemy.future import select
from fastapi.encoders import jsonable_encoder

class CRUDArena(CRUDBase[Arena, ArenaCreate, ArenaUpdate]):
    async def create_arena(self, db: AsyncSession, input: ArenaCreate) -> Arena:
        return await self.create(db, obj_in=input)

    async def get_all_arena(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Arena]:
        return await self.get_multi(db, skip=skip, limit=limit)

    # async def delete_arena(self, db: AsyncSession, arena_id: int) -> Optional[Arena]:
    #     return await self.remove(db, model_id=arena_id)
        
    async def delete_all_arenas(self, db: AsyncSession):
        async with db.begin():  # Start a transaction
            await db.execute(text("DELETE FROM arena")) 
    
    async def get_empty_arena(self, db: AsyncSession, *, game_id: str, entry_fee: int, limit: int) -> List[Arena]:
        today = datetime.datetime.now()
        delta = datetime.timedelta(minutes=1439)
        ago = today - delta

        ex = await db.execute(
            select(self.model)
            .filter(
                self.model.game_id == game_id,
                self.model.current_users > 0,
                self.model.current_users < limit,
                self.model.max_users.isnot(None),
                self.model.max_users == limit,
                self.model.entry_fee == entry_fee,
                self.model.created_at >= ago
            )
            .order_by(self.model.created_at.asc())
            .limit(100)  # Limit the results to only the oldest record
        )

        return ex.scalars().all()
    
arena = CRUDArena(Arena)
