from fastapi import FastAPI, HTTPException, Header, Depends
from fast_api_airguardian.settings import settings
import httpx
from typing import List
from fast_api_airguardian import schemas
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fast_api_airguardian.model import Violation
from .database import get_async_db, create_tables_sync 
import time
from .model import Violation
from sqlalchemy.exc import OperationalError
import logging

logger = logging.getLogger(__name__)

NO_FLYING_ZONE = 1000

app = FastAPI()

@app.on_event("startup")
def startup_event():
    """Docker-aware startup with retry logic"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            create_tables_sync()
            logger.info("✅ Database tables ready")
            break
        except OperationalError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"⚠️ Database not ready, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                logger.error("❌ Failed to connect to database after multiple attempts")
                raise


@app.get("/health")
def health():
    return {"success": "ok"}


@app.get("/drones", response_model=List[schemas.Drone])
async def get_drones():
    try:
        logger.info(f"📡 Fetching drones from {str(settings.base_url)}")
        async with httpx.AsyncClient() as client:
            response = await client.get(str(settings.base_url))
            response.raise_for_status()
            data = response.json()
    except Exception as e:
            logger.error(f"❌ Drone fetch error: {e}")
            raise HTTPException(status_code=503, detail="Drone data unavailable")
    try:
        drones = [schemas.Drone(**drone) for drone in data]
        return drones
    except ValidationError as e:
        logger.error(f"❌ Validation error while parsing drone data: {e}")
        raise HTTPException(status_code=500, detail="Invalid drone data received")


@app.get("/nfz", response_model=list[schemas.ViolationSchema])
async def read_violations(
    db: AsyncSession = Depends(get_async_db),
    x_secret: str = Header(None)
):
    if x_secret != settings.api_secret:
        raise HTTPException(status_code=401, detail="Invalid secret key")
        
    result = await db.execute(select(Violation))
    violations = result.scalars().all()

    if not violations:
        raise HTTPException(status_code=404, detail="No NFZ violations found")
    return violations