from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base
from .settings import settings

# Single Base for all models
Base = declarative_base()

# Celery needs sync connections for blocking operations 
sync_engine = create_engine(
    str(settings.database_url_sync), 
    echo=True,              #disable in production
    pool_size=5,
    pool_timeout=30,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    async_strategy=True     # Async driver (asyncpg)
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# FastAPI needs async connections for concurrent I/O
async_engine = create_async_engine(
    str(settings.database_url_async), 
    echo=True,              #disable in production
    pool_size=5,
    pool_overflow=10,
    pool_timeout=5,
    pool_recyle=3600,
    sync_strategy=True      # Sync driver (psycopg2)
)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


def get_sync_db():
    """Sync session for Celery tasks"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Get an async session for FastAPI endpoints"""
    async with AsyncSessionLocal() as session:
        yield session

def get_db_session():
    """Get a sync session for Celery tasks"""
    return SyncSessionLocal()

def create_tables_sync():
    """Create all tables using sync engine"""
    Base.metadata.create_all(bind=sync_engine)