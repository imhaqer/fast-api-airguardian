from fastapi import FastAPI, HTTPException
from fast_api_airguardian.settings import settings
import httpx
from pydantic import BaseModel
from typing import List
from fast_api_airguardian import schemas
from pydantic import ValidationError

class Item(BaseModel):
    name: str
    quantity: int

# BASE_URL = str(settings.base_url)

app = FastAPI()

@app.get("/health")
def health():
    return {"success": "ok"}

@app.get("/drones", response_model=List[schemas.Drone])
async def get_drones():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(str(settings.base_url))
            response.raise_for_status()
            data = response.json()
    except Exception as e:
            raise HTTPException(status_code=503, detail="Drone data unavailable")
    try:
        drones = [schemas.Drone(**drone) for drone in data]
        return drones
    except ValidationError as e:
            raise HTTPException(status_code=500, detail="Invalid drone data received")

"""@app.get("nfz/")
async def get_violation():"""
     