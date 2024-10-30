import asyncio
from app.database.initialise import initialise
from app.database.session import AsyncSessionLocal

async def init() -> None:
    async with AsyncSessionLocal() as session:
        await initialise(session)

def main() -> None:
    asyncio.run(init())

if __name__ == "__main__":
    main()
