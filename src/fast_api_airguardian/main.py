from fastapi import FastAPI, HTTPException, Header, Depends
from fast_api_airguardian.settings import settings
import httpx
from pydantic import BaseModel
from typing import List
from fast_api_airguardian import schemas
from pydantic import ValidationError
# from fast_api_airguardian.model import Violation
import math
import asyncpg
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fast_api_airguardian.database import get_db
import signal
from sqlalchemy.future import select
from fast_api_airguardian.model import ViolationAsync as Violation

import asyncio

NO_FLYING_ZONE = 1000

# BASE_URL = str(settings.base_url)

app = FastAPI()

#graceful shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down gracefully...")
    # Clean up resources

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
    db: AsyncSession = Depends(get_db),
    x_sercret: str = Header(None)
):
    if x_sercret != settings.api_secret:
        raise HTTPException(status_code=401, detail="Invalid secret key")
        
    result = await db.execute(select(Violation))
    violations = result.scalars().all()

    if not violations:
        raise HTTPException(status_code=404, detail="No NFZ violations found")

    return violations