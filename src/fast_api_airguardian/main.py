from fastapi import FastAPI, HTTPException, Header, Depends
from fast_api_airguardian.settings import settings
import httpx
from typing import List
from fast_api_airguardian import schemas
from pydantic import ValidationError
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fast_api_airguardian.database import get_async_db
from sqlalchemy.future import select
from fast_api_airguardian.model import Violation
from .database import get_async_db, create_tables_sync 
import time
from .model import Violation
from sqlalchemy.exc import OperationalError

NO_FLYING_ZONE = 1000

# BASE_URL = str(settings.base_url)

app = FastAPI()

#graceful shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down gracefully...")
    # Clean up resources
@app.on_event("startup")
def startup_event():
    """Docker-aware startup with retry logic"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            create_tables_sync()
            print("✅ Database tables ready")
            break
        except OperationalError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⚠️ Database not ready, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print("❌ Failed to connect to database after multiple attempts")
                raise


@app.get("/health")
def health():
    return {"success": "ok"}

@app.get("/drones", response_model=List[schemas.Drone])
async def get_drones():
    try:
        print(f"📡 Fetching drones from {str(settings.base_url)}")
        async with httpx.AsyncClient() as client:
            response = await client.get(str(settings.base_url))
            response.raise_for_status()
            data = response.json()
            print("📦 Raw API response:")
            print(data)
    except Exception as e:
            print(f"❌ Drone fetch error: {e}")
            raise HTTPException(status_code=503, detail="Drone data unavailable")
    try:
        drones = [schemas.Drone(**drone) for drone in data]
        return drones
    except ValidationError as e:
            print("❌ Validation error while parsing drone data:")
            print(e)
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