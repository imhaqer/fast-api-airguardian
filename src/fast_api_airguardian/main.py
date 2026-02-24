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

app = FastAPI(
    title="Drone Monitoring API",
    description="API for monitoring drones and NFZ violations",
    version="1.0.0"
)

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
                backoff_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"⚠️ Database not ready, retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(backoff_time)
            else:
                logger.error("❌ Failed to connect to database after multiple attempts")
                raise


@app.get("/health")
def health():
    """
    Check API status and connectivity.

    Returns:
        A simple status message to confirm the API is working.
    """
    return {"success": "ok"}


@app.get("/drones", response_model=List[schemas.Drone])
async def get_drones():
    """
    Get real-time drone positions.

    Fetches current drone data from an external service in real-time.
    Each call return the most up-to-date positions of all active drones.

    Raises:
        HTTPException 503: Service unavailable
        HTTPException 500: Data validation failed

    Returns:
        List[Drone]: Real-time list of all the active drones with current positions
    """
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
    """
    Get all NFZ (No-Fly Zone) violations.

    Requires a secret key for API authentication (in header)
    db: Database connection (automatically handled)

    Raises:
        HTTPException 401: Invalid secret key
        HTTPException 200: No violations found

    Return: 
        List[ViolationSchema]: All recorded NFZ violation incidents.
    """
    if x_secret != settings.api_secret:
        raise HTTPException(status_code=401, detail="Invalid secret key")
        
    result = await db.execute(select(Violation))
    violations = result.scalars().all()

    if not violations:
        raise HTTPException(status_code=200, detail="No NFZ violations found")
    return violations