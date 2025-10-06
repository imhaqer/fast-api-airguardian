from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base
from .settings import settings

# Single Base for all models
Base = declarative_base()

# Sync engine for Celery and table creation
sync_engine = create_engine(
    str(settings.database_url_sync), 
    echo=True,
    pool_size=5,  # ✅ Added connection pooling
    max_overflow=20,
    pool_pre_ping=True
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async engine for FastAPI
async_engine = create_async_engine(
    str(settings.database_url_async), 
    echo=True,
    pool_size=5  # ✅ Connection pooling for async too
)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# ✅ FIXED: For Celery tasks (SYNC)
def get_sync_db():
    """Sync session for Celery tasks"""
    db = SyncSessionLocal()  # ✅ Use SyncSessionLocal, not AsyncSessionLocal
    try:
        yield db
    finally:
        db.close()

# ✅ For FastAPI endpoints (ASYNC)
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

# ✅ Simple session getter for Celery
def get_db_session():
    """Get a sync session for Celery tasks"""
    return SyncSessionLocal()

# ✅ Table creation function
def create_tables_sync():
    """Create all tables using sync engine"""
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Tables created successfully.")