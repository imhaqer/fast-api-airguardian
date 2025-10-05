import asyncio
from fast_api_airguardian.database import engine
from fast_api_airguardian.model import Base

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
print("✅ Tables created successfully.")
asyncio.run(create_tables())
print("✅ Tables created successfully.")