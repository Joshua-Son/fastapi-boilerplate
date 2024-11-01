from pydantic import BaseModel, Field
import uuid
from typing import Optional
from datetime import datetime, timezone

class GameStreamBase(BaseModel):
    id: Optional[int] # ip address name join with 00
    name: Optional[str]
    address: Optional[str] # guac address
    addrapi: Optional[str] # ip address with port 8000
    status: Optional[str]
    game_id: Optional[str]
    player_id: Optional[str]
    started: Optional[datetime]
    ended: Optional[datetime]
    time_created: Optional[datetime]
    time_updated: Optional[datetime]

class GameStreamCreate(GameStreamBase):
    id: int
    name: str
    address: str
    addrapi: str
    status: str

class GameStreamUpdate(GameStreamBase):
    id: int
    status: str
    pass

class GameStreamReserve(BaseModel):
    game_id: str
    player_id: str
    nation: str

class GameStreamReleaseQuit(BaseModel):
    id: int
    player_id: str


class GameStreamResponse(GameStreamBase):
    class Config:
        from_attributes = True