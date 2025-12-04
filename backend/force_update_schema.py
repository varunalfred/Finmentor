import asyncio
from models.database import Base, MarketIndex, StockPrice
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def force_update():
    print(f"Connecting to database...")
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("Dropping old market tables...")
        await conn.execute(text("DROP TABLE IF EXISTS market_indices CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS stock_prices CASCADE"))
        
        print("Recreating tables with new schema...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables updated successfully!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(force_update())
