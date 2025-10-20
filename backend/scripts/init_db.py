"""
Initialize database tables and pgvector extension
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config import settings
from models.document import Base as DocumentBase
from models.session import Base as SessionBase
from models.user import Base as UserBase


async def init_database():
    """Initialize database with tables and extensions"""

    print("🚀 Initializing ReadPilot database...")
    print(f"   Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")

    # Create engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO
    )

    try:
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"\n✅ Connected to database")
            print(f"   Version: {version[:50]}...")

            # Enable pgvector extension (PostgreSQL only)
            if 'postgresql' in settings.DATABASE_URL:
                print("\n📦 Installing pgvector extension...")
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    print("   ✅ pgvector extension enabled")
                except Exception as e:
                    print(f"   ⚠️  Could not enable pgvector: {e}")
                    print("   Note: pgvector must be installed on PostgreSQL server")

        # Create all tables
        print("\n🔨 Creating database tables...")
        async with engine.begin() as conn:
            # Drop all tables (optional, for development)
            # await conn.run_sync(DocumentBase.metadata.drop_all)
            # await conn.run_sync(SessionBase.metadata.drop_all)
            # await conn.run_sync(UserBase.metadata.drop_all)

            # Create tables in correct order (respecting foreign keys)
            # 1. Users first (no dependencies)
            await conn.run_sync(UserBase.metadata.create_all)
            # 2. Documents (depends on users)
            await conn.run_sync(DocumentBase.metadata.create_all)
            # 3. Sessions (depends on users and documents)
            await conn.run_sync(SessionBase.metadata.create_all)

            print("   ✅ Tables created successfully")

        # List created tables
        print("\n📋 Database tables:")
        async with engine.connect() as conn:
            if 'postgresql' in settings.DATABASE_URL:
                result = await conn.execute(text("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """))
            else:  # SQLite
                result = await conn.execute(text("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table'
                    ORDER BY name
                """))

            tables = result.fetchall()
            for table in tables:
                print(f"   - {table[0]}")

        print("\n✅ Database initialization complete!")

    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
