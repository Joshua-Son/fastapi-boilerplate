from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database.base_class import Base

class Participation(Base):
    id = Column(Integer, primary_key=True, index=True)
    arena_id = Column(UUID(as_uuid=True), ForeignKey("arena.id"), nullable=False)  # ForeignKey reference
    user_uuid = Column(UUID(as_uuid=True))
    challenge = Column(Integer)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Define the relationship to participants
    arena = relationship("Arena", back_populates="participation")
