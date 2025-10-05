from pydantic import BaseModel
from datetime import datetime


class Drone(BaseModel):
    id: str
    owner_id: int
    x: int  # API returns 'x', not 'position_x'
    y: int  # API returns 'y', not 'position_y'  
    z: int  # API returns 'z', not 'position_z'


class ViolationSchema(BaseModel):
    drone_id: str
    timestamp: datetime
    position_x: int
    position_y: int
    position_z: int
    distance_from_center: int
    owner_first_name: str
    owner_last_name: str
    owner_ssn: str
    owner_phone: int

    class Config:
        from_attributes = True #* 'orm_mode' has been renamed to 'from_attributes'
   # severity: str

