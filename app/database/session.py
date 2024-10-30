from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core import settings

# Use the async engine without pool_pre_ping
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)

# Create an async session
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
