from pydantic import BaseModel

class Drone(BaseModel):
    id: str
    owner_id: int
    x: float
    y: float
    z: float