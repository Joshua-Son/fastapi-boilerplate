from sqlalchemy.ext.asyncio import AsyncSession

async def initialise(db: AsyncSession) -> None:
    # Write database initialization queries using the async session.
    pass
