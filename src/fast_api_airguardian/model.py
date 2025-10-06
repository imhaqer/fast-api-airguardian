# fast_api_airguardian/model.py

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base as sync_declarative_base
from sqlalchemy.ext.declarative import declarative_base as async_declarative_base

from .database import Base 

# Create two declarative bases — one for async, one for sync
"""BaseSync = sync_declarative_base()
BaseAsync = async_declarative_base()

# --- SYNC model for Celery (uses regular SQLAlchemy Session) ---
class ViolationSync(BaseSync):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drone_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    position_x = Column(Integer)
    position_y = Column(Integer)
    position_z = Column(Integer)
    distance_from_center = Column(Integer)
    owner_first_name = Column(String)
    owner_last_name = Column(String)
    owner_ssn = Column(String)
    owner_phone = Column(String)

    class Config:
        orm_mode = True


# --- ASYNC model for FastAPI (uses AsyncSession) ---
class ViolationAsync(BaseAsync):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drone_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    position_x = Column(Integer)
    position_y = Column(Integer)
    position_z = Column(Integer)
    distance_from_center = Column(Integer)
    owner_first_name = Column(String)
    owner_last_name = Column(String)
    owner_ssn = Column(String)
    owner_phone = Column(String)

    class Config:
        orm_mode = True
"""
class Violation(Base):  # ✅ SINGLE model for both Celery and FastAPI
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drone_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    position_x = Column(Integer)
    position_y = Column(Integer)
    position_z = Column(Integer)
    distance_from_center = Column(Integer)
    owner_first_name = Column(String)
    owner_last_name = Column(String)
    owner_ssn = Column(String)
    owner_phone = Column(String)