from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import Optional

class ParticipationBase(BaseModel):
    id: int
    user_uuid: uuid.UUID  # Use UUID type
    arena_id: int
    score: Optional[int] = 0
    status: str  # e.g., "playing", "finished"
    joined_at: datetime

class ParticipationCreate(ParticipationBase):
    joined_at: datetime = Field(default_factory=datetime.now)

class ParticipationUpdate(ParticipationBase):
    score: Optional[int] = None
    status: Optional[str] = None

class ParticipationResponse(ParticipationBase):
    class Config:
        from_attributes = True  # Updated for V2
