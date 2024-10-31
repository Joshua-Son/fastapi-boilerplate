from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional

class ParticipationBase(BaseModel):
    id: int
    user_uuid: uuid.UUID  # Use UUID type
    arena_id: uuid.UUID
    joined_at: datetime
    challenge: int

class ParticipationCreate(BaseModel):
    arena_id: uuid.UUID
    user_uuid: uuid.UUID
    challenge: int

class ParticipationDeleteAPI(BaseModel):
    arena_id: str
    user_id: str
    challenge: float


class ParticipationUpdate(ParticipationBase):
    pass

class ParticipationResponse(ParticipationBase):
    class Config:
        from_attributes = True  # Updated for V2
