from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.gamestream import GameStream
from app.schemas import GameStreamCreate, GameStreamUpdate, GameStreamReserve

from sqlalchemy.dialects.postgresql import insert
from fastapi.encoders import jsonable_encoder
from sqlalchemy.future import select

class CRUDGamestream(CRUDBase[GameStream, GameStreamCreate, GameStreamUpdate]):
    async def get_gstream_all(self, db: AsyncSession) -> List[GameStream]:
        result = await db.execute(select(self.model))
        return result.scalars().all()
  
    # async def get_by_user_id(self, db: AsyncSession, player_id: str) -> Optional[GameStream]:
    #     result = await db.execute(select(self.model).where(self.model.player_id == player_id))
    #     return result.scalars().first()
    
    # async def get_idle_gstream(self, db: AsyncSession) -> Optional[GameStream]:
    #     result = await db.execute(select(self.model).where(self.model.status == "idle"))
    #     return result.scalars().first()
    
    async def upsert_gstream(self, db: AsyncSession, input: GameStreamCreate) -> GameStream:
        obj_in_data = jsonable_encoder(input)
        stmt = insert(self.model).values(**obj_in_data)

        # Define what to do on conflict (update the existing record)
        stmt = stmt.on_conflict_do_update(
            index_elements=['id', 'addrapi', 'address'],  # Unique constraint column(s)
            set_={
                "status": obj_in_data.get("status"),
            }
        )
        
        await db.execute(stmt)  # Make sure to await this
        await db.commit()

        return self.model(**obj_in_data)
    
gamestream = CRUDGamestream(GameStream)