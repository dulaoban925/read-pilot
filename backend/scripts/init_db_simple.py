"""
Simple database initialization using raw SQL
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg


async def init_database():
    """Initialize database with tables using raw SQL"""

    print("🚀 Initializing ReadPilot database (simple mode)...")

    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='anker',
        database='readpilot'
    )

    try:
        # Test connection
        version = await conn.fetchval('SELECT version()')
        print(f"\n✅ Connected to database")
        print(f"   Version: {version[:80]}...")

        # Create tables
        print("\n🔨 Creating database tables...")

        # Users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT,
                password_hash TEXT,
                preferences JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ Created table: users")

        # Documents table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id),
                title TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                document_type TEXT,
                page_count INTEGER DEFAULT 0,
                word_count INTEGER DEFAULT 0,
                language TEXT DEFAULT 'zh',
                summary JSONB,
                processing_status TEXT DEFAULT 'pending',
                indexed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ Created table: documents")

        # Document chunks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT REFERENCES documents(id),
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                page_number INTEGER,
                embedding_vector JSONB,
                chunk_metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ Created table: document_chunks")

        # Sessions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id),
                document_id TEXT REFERENCES documents(id),
                title TEXT,
                session_type TEXT DEFAULT 'chat',
                context_variables JSONB DEFAULT '{}'::jsonb,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP
            )
        """)
        print("   ✅ Created table: sessions")

        # Messages table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT REFERENCES sessions(id),
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                agent_name TEXT,
                message_metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ Created table: messages")

        # Create indices
        print("\n📊 Creating indices...")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_document_id ON sessions(document_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)")
        print("   ✅ Indices created")

        # List tables
        print("\n📋 Database tables:")
        tables = await conn.fetch("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        for table in tables:
            print(f"   - {table['tablename']}")

        print("\n✅ Database initialization complete!")
        print("\n📝 Note: pgvector extension is not installed.")
        print("   To install:")
        print("   1. brew install pgvector")
        print("   2. psql readpilot -c 'CREATE EXTENSION vector;'")

    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_database())
