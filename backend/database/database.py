"""
Database connection and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, event
from backend.core.config import settings
from backend.database.models import Base


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database: create tables and FTS5 virtual table
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Create FTS5 virtual table for full-text search
        await conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
                episode_id UNINDEXED,
                title,
                description,
                podcast_name,
                transcript_text,
                tags,
                content=''
            )
        """))

        # Create triggers to keep FTS5 in sync
        await conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS episodes_fts_insert
            AFTER INSERT ON episodes
            BEGIN
                INSERT INTO episodes_fts(episode_id, title, description, podcast_name, tags)
                VALUES (new.id, new.title, new.description, new.podcast_name, new.tags);
            END
        """))

        await conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS episodes_fts_update
            AFTER UPDATE ON episodes
            BEGIN
                UPDATE episodes_fts
                SET title = new.title,
                    description = new.description,
                    podcast_name = new.podcast_name,
                    tags = new.tags
                WHERE episode_id = new.id;
            END
        """))

        await conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS episodes_fts_delete
            AFTER DELETE ON episodes
            BEGIN
                DELETE FROM episodes_fts WHERE episode_id = old.id;
            END
        """))

        # Create trigger for transcript FTS
        await conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS transcript_fts_insert
            AFTER INSERT ON transcripts
            BEGIN
                UPDATE episodes_fts
                SET transcript_text = new.full_text
                WHERE episode_id = new.episode_id;
            END
        """))

        await conn.commit()


async def close_db():
    """
    Close database connections
    """
    await engine.dispose()
