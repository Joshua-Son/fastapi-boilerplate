from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database.base_class import Base

class GameStream(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    addrapi = Column(String, nullable=True)
    status = Column(String, nullable=False)

    game_id = Column(String, nullable=True)
    player_id = Column(String, nullable=True)
    started = Column(DateTime(timezone=True), nullable=True)
    ended = Column(DateTime(timezone=True), nullable=True)

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())