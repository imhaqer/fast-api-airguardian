from src.fast_api_airguardian.celery import celery_app
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import asyncio
from datetime import datetime
import math
from fast_api_airguardian.settings import settings
from .schemas import Drone
from pydantic import ValidationError
import requests
from fast_api_airguardian.model import Violation
from .database import get_db_session 
import logging

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10.0
MAX_REPEAT = 3
NO_FLY_ZONE_RADIUS = 1000  # units

# validate coordinates

"""async def fetch_drone_data() -> list[dict]:
    for attempt in range(MAX_REPEAT):
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIME) as client:"""
def calculate_distance(x: int, y: int) -> int:
    return math.sqrt(x**2 + y**2)

def is_in_nfz(x: int, y: int) -> bool:
    distance = math.sqrt(x**2 + y**2)
    return distance <= NO_FLY_ZONE_RADIUS

# --- Data fetch ---
def fetch_drones_data() -> list[dict]:
    for attempt in range(MAX_REPEAT):
        try:
            response = requests.get(str(settings.base_url), timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1}/{MAX_REPEAT} failed: {e}")
    logger.error("❌ Failed to fetch drone data after multiple attempts.")
    return []

def get_drone_owner_info(owner_id: int) -> dict:
    try:
        if not owner_id:
            return {}
        response = requests.get(f"https://drones-api.hive.fi/users/{owner_id}", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching owner info: {e}")
        return {}

def store_violation_to_db(drone_data: dict, owner_info: dict):
    """1st try Create a NEW database session for each violation"""
    """2nd try Create a NEW database session for each violation - NO db parameter!"""
    """SYNC version - use regular Session, not AsyncSession"""
    # Create sync engine and session
    # ❌ Creating new engine for each violation:
    #engine = create_engine(str(settings.database_url_sync))

    """✅ CORRECT: Use shared database engine and connection pool"""
    db = get_db_session()  # ✅ Get session from shared pool
    
    try:
        x = drone_data.get("x", 0)
        y = drone_data.get("y", 0)
        distance = calculate_distance(x, y)

        # ✅ Fixed variable name (violations → violation)
        violation = Violation(
            drone_id=drone_data.get("id", ""),
            timestamp=datetime.utcnow(),
            position_x=x,
            position_y=y,
            position_z=drone_data.get("z", 0),
            distance_from_center=distance,
            owner_first_name=owner_info.get("first_name", ""),
            owner_last_name=owner_info.get("last_name", ""),
            owner_ssn=owner_info.get("social_security_number", ""),
            owner_phone=owner_info.get("phone_number", "")
        )
        db.add(violation)
        db.commit()
        db.refresh(violation)
        logger.info(f"✅ Violation stored for drone {drone_data.get('id')}")
        return violation     
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error storing violation: {e}")
        raise
    finally:
        db.close()  # ✅ Always close session
   # return violations


def process_nfz_violations(): # without passing a session
    logger.info("🚁 Starting NFZ check task")

    drone_data_raw = fetch_drones_data()

    if not drone_data_raw:
        logger.info("⚠️ No drone data received.")
        return 0

    try: 
        # ✅ Now this will work because Drone model matches API fields
        drones = [Drone(**drone) for drone in drone_data_raw]
        logger.info(f"✅ Successfully validated {len(drones)} drones")
            
    except ValidationError as e:
        logger.error("❌ Validation error while parsing drone data: %s", e)
        return   # Since this is a background task, just log and return (no HTTPException)
    
    violations_detected = 0
    for drone in drones:
        # ✅ Use the correct field names: drone.x, drone.y (not position_x, position_y)
        if is_in_nfz(drone.x, drone.y):
            distance = calculate_distance(drone.x, drone.y)
            logger.warning(f"🚨 NFZ Violation! Drone id: {drone.id}")
            
            owner_info = get_drone_owner_info(drone.owner_id) if drone.owner_id else {}
            
            # Convert to dict for your existing store function
            drone_dict = drone.dict()
            store_violation_to_db(drone_dict, owner_info)  # No db paramete
            violations_detected += 1
    logger.info(f"NFZ check completed. Found {violations_detected} violations.")
    return violations_detected


"""@celery_app.task(name="src.fast_api_airguardian.tasks.fetch_drone_positions_task")
def fetch_drone_positions_task():
   

    async def task_main():
        # Create an async session
        async with async_session() as session:
            await process_nfz_violations(session)

    # Run the async function in the event loop
    asyncio.run(task_main())"""


@celery_app.task(name="src.fast_api_airguardian.tasks.fetch_drone_positions_task")
def fetch_drone_positions_task():
    """
    Celery task that runs NFZ violation processing
    """
    """async def task_main():
        return process_nfz_violations()  # No session parameter needed
"""
    # Run the async function
    try:
       # result = asyncio.run(task_main())
        result = process_nfz_violations()  # Direct sync call - no async!
        logger.info(f"🎉 Celery task completed. Violations found: {result}")
        return {
            "success": True,
            "violations_detected": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Celery task failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
    
# USE SYNC CODE FOR CELERY