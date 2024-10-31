from sqlalchemy import Column, Integer, Enum, DateTime, UUID
from sqlalchemy.sql import func  # Import the func module
from sqlalchemy.orm import relationship

from app.database.base_class import Base
    
class Arena(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, server_default=func.gen_random_uuid())
    entry_fee = Column(Integer, nullable=True)
    game_id = Column(UUID(as_uuid=True), nullable=False)
    max_users = Column(Integer, nullable=True)  # Nullable for tournaments
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    current_users = Column(Integer, nullable=False, server_default='0')

    # Define the relationship to participants
    # participants = relationship("Participation", back_populates="arena", cascade="all, delete-orphan")