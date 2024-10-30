from sqlalchemy import Column, Integer, Enum, DateTime, UUID
from sqlalchemy.sql import func  # Import the func module
from sqlalchemy.orm import relationship

import uuid

from app.database.base_class import Base
    
class Arena(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    entry_fee = Column(Integer, nullable=True)
    game_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    max_users = Column(Integer, nullable=True)  # Nullable for tournaments
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    current_users = Column(Integer, default=0, nullable=False)

    # Define the relationship to participants
    # participants = relationship("Participation", back_populates="arena", cascade="all, delete-orphan")