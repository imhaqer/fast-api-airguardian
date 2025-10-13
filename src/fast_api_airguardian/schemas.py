from pydantic import BaseModel, ConfigDict
from datetime import datetime


class Drone(BaseModel):
    id: str
    owner_id: int
    x: int
    y: int
    z: int


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

    model_config = ConfigDict(from_attributes=True)  # modern way

