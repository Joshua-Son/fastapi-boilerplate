from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database.base_class import Base

class Participation(Base):
    id = Column(Integer, primary_key=True, index=True)
    arena_id = Column(Integer, ForeignKey("arenas.id"), nullable=False)  # ForeignKey reference
    user_uuid = Column(String, index=True)
    score = Column(Integer, default=0)
    status = Column(String)  # e.g., "playing", "finished"
    room_id = Column(Integer, ForeignKey("arenas.id"), nullable=False)  # Adjust if necessary
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Define the relationship to arena
    # arena = relationship("Arena", back_populates="participants")