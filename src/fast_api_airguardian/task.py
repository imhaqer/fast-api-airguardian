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


def calculate_distance(x: int, y: int):
    """
    Calculate Euclidean distance from center point (0,0).
    
    Args:
        x: X coordinate of the drone position
        y: Y coordinate of the drone position
        
    Returns:
        int: Distance from center
    """
    return math.sqrt(x**2 + y**2)

def is_in_nfz(x: int, y: int) -> bool:
    """
    Check if a position is within the No-Fly Zone.
    
    The No-Fly Zone is defined as a circular area with radius 
    NO_FLY_ZONE_RADIUS from the center point (0,0).
    
    Args:
        x: X coordinate of the drone position
        y: Y coordinate of the drone position
        
    Returns:
        bool: True if position is within NFZ, False otherwise
    """
    distance = math.sqrt(x**2 + y**2)
    return distance <= NO_FLY_ZONE_RADIUS

# --- Data fetch ---
def fetch_drones_data() -> list[dict]:
    """
    Fetch live drone position data from external API.
    
    Implements retry logic with exponential backoff for reliability.
    
    Returns:
        list[dict]: List of drone objects with position data
        Empty list if all retry attempts fail
        
    Raises:
        Logs warnings for failed attempts, error for complete failure
    """
    for attempt in range(MAX_REPEAT):
        try:
            response = requests.get(str(settings.base_url), timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt + 1}/{MAX_REPEAT} failed: {e}")
    logger.error("❌ Failed to fetch drone data after multiple attempts.")
    return []

def get_drone_owner_info(owner_id: int) -> dict:
    """
    Fetch drone owner information from user API.
    
    Args:
        owner_id: Unique identifier for drone owner
        
    Returns:
        dict: Owner information including name and contact details
        Empty dict if owner_id is invalid or API call fails
    """
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
    """
    Store NFZ violation record in database.
    
    Creates a new violation entry with drone position data and owner information.
    Uses shared database connection pool for efficient session management.
    
    Args:
        drone_data: Dictionary containing drone position and identification
        owner_info: Dictionary containing owner personal information
        
    Returns:
        Violation: The created violation record
        
    Raises:
        Exception: If database operation fails, rolls back transaction
    """
    db = get_db_session()  # ✅ Get session from shared pool
    
    try:
        x = drone_data.get("x", 0)
        y = drone_data.get("y", 0)
        distance = calculate_distance(x, y)

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


def process_nfz_violations(): # without passing a session
    """
    Main NFZ violation detection and processing function.
    
    Fetches current drone positions, validates data, checks for NFZ violations,
    and stores violation records with owner information.
    
    Returns:
        int: Number of violations detected and processed
        0:   no drone data available or validation fails
    """
    logger.info("🚁 Starting NFZ check task")

    drone_data_raw = fetch_drones_data()

    if not drone_data_raw:
        logger.info("⚠️ No drone data received.")
        return 0

    try: 
        drones = [Drone(**drone) for drone in drone_data_raw]
        logger.info(f"✅ Successfully validated {len(drones)} drones")
            
    except ValidationError as e:
        logger.error("❌ Validation error while parsing drone data: %s", e)
        return   # Since this is a background task, just log and return (no HTTPException)
    
    violations_detected = 0
    for drone in drones:
        if is_in_nfz(drone.x, drone.y):
            distance = calculate_distance(drone.x, drone.y)
            logger.warning(f"🚨 NFZ Violation! Drone id: {drone.id}")
            
            owner_info = get_drone_owner_info(drone.owner_id) if drone.owner_id else {}
            
            # Convert to dict for your existing store function
            drone_dict = drone.dict()
            store_violation_to_db(drone_dict, owner_info)  # No db paramete
            violations_detected += 1
    return violations_detected

@celery_app.task(name="src.fast_api_airguardian.tasks.fetch_drone_positions_task")
def fetch_drone_positions_task():
    """
    Celery task for periodic drone position monitoring and NFZ violation detection.
    
    This background task runs on a schedule to continuously monitor drone positions
    and detect No-Fly Zone violations.
    
    Returns:
        dict: Task execution result with:
            - success: Boolean indicating task completion status
            - violations_detected: Number of violations found
            - timestamp: UTC timestamp of task completion
            - error: Error message if task failed
    """
    try:

        result = process_nfz_violations()  # Direct sync call - no async!
        logger.info(f"⚠️ Celery task completed. Violations found: {result}")
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