import asyncio
from models.database import Base, MarketIndex, StockPrice
from models.document import UserDocument  # Import to register with Base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def check_data():
    print(f"Connecting to database...")
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        pass # Just to test connection
        
    async with engine.connect() as session:
        print("Checking MarketIndex count...")
        # Try fetching raw rows
        result = await session.execute(select(MarketIndex))
        rows = result.all()
        print(f"Row count: {len(rows)}")
        
        if rows:
            print(f"First row raw: {rows[0]}")
            # Check if it's a tuple with an object or just a value
            first_item = rows[0][0]
            print(f"First item type: {type(first_item)}")
            
            if hasattr(first_item, 'history'):
                print(f"History found! Length: {len(first_item.history) if first_item.history else 0}")
                print(f"Sample: {first_item.history[:2] if first_item.history else 'None'}")
            else:
                print("No history attribute on first item.")
                
        # Try getting specific item
        print("\nTrying direct get...")
        # We need a session with ORM for get(), connect() gives a connection.
        # Let's use AsyncSession(engine)
        from sqlalchemy.ext.asyncio import AsyncSession
        async with AsyncSession(engine) as orm_session:
            idx = await orm_session.get(MarketIndex, "^NSEI")
            if idx:
                print(f"Direct get success: {idx.symbol}")
                print(f"History len: {len(idx.history) if idx.history else 0}")
            else:
                print("Direct get failed.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_data())
