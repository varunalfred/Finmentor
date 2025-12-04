import asyncio
from sqlalchemy import text
from services.database import db_service

async def run_migration():
    print("🔄 Starting database migration...")
    # Create a new connection for the migration
    async with db_service.engine.connect() as conn:
        try:
            # Check if column exists
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='profile_picture_url'"
            ))
            if result.fetchone():
                print("✅ Column 'profile_picture_url' already exists.")
            else:
                print("➕ Adding 'profile_picture_url' column...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(500)"))
                await conn.commit()
                print("✅ Migration successful!")
        except Exception as e:
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
