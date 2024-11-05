from pydantic import BaseModel, Field
import uuid
from typing import Optional, Any
from datetime import datetime, timezone


class ArenaBase(BaseModel):
    id: Optional[uuid.UUID]
    game_id: Optional[uuid.UUID]
    max_users: Optional[int]
    entry_fee: Optional[int]
    created_at: Optional[datetime]
    current_users: Optional[int]


class ArenaCreate(BaseModel):
    game_id: uuid.UUID
    max_users: int
    entry_fee: Optional[int]

class ArenaMultiCreateAPI(BaseModel):
    game_id: str
    user_id: str
    entryFee: float
    is_practice: bool
    user_limit: int


class SignalAPI(BaseModel):
    arena_id: str
    player_id: str
    status: str
    score: str
    stream_id: str



class ArenaUpdate(ArenaBase):
    game_id: Optional[uuid.UUID] = None
    max_users: Optional[int] = None

class ArenaResponse(ArenaBase):
    class Config:
        from_attributes = True  # Updated for V2
