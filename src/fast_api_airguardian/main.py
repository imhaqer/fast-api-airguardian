from fastapi import FastAPI, HTTPException
from fast_api_airguardian.settings import settings
import httpx
import logging

BASE_URL = str(settings.base_url)

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.get("/health")
def health():
    return {"success": "ok"}
    
""""
@app.get("/invalid_health")
async def health():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get((BASE_URL))  #complains if passed non-string
        if (response.status_code == 200):
            return {"success": "ok"}
        else:
            raise HTTPException(status_code=503, detail="unavailable")
    except httpx.ReadError:
            raise HTTPException(status_code=503, detail="Failed to connect to external service")
"""
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def debug(msg: str):
    print(f"{BLUE}DEBUG: {msg}{RESET}")


def info(msg: str):
    print(f"{GREEN}INFO: {msg}{RESET}")

def error(msg: str):
    print(f"{RED}ERROR: {msg}{RESET}")

@app.get("/drones")
async def get_drones():
    debug("Starting /drones endpoint")
    info("Calling external drone API...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL)
        info(f"External API responded with status {response.status_code}")
        response.raise_for_status()  # Raises error for 4xx/5xx responses
        debug("Returning JSON response from external API")
        return response.json()
    except httpx.RequestError as e:
        error(f"Request to external drone API failed: {e}")
        raise HTTPException(status_code=503, detail="Failed to fetch drone data")
    except httpx.HTTPStatusError as e:
        error(f"External drone API returned error status: {e}")
        raise HTTPException(status_code=e.response.status_code, detail="External API error")