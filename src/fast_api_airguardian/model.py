# fast_api_airguardian/model.py

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base as sync_declarative_base
from sqlalchemy.ext.declarative import declarative_base as async_declarative_base

from .database import Base 

class Violation(Base):  # ✅ SINGLE model for both Celery and FastAPI
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drone_id                = Column(String, index=True, nullable=False)
    timestamp               = Column(DateTime, index=True, nullable=False)
    position_x              = Column(Integer, nullable=False)
    position_y              = Column(Integer, nullable=False)
    position_z              = Column(Integer, nullable=False)
    distance_from_center    = Column(Integer, nullable=False)
    owner_first_name        = Column(String, nullable=False)
    owner_last_name         = Column(String, nullable=False)
    owner_ssn               = Column(String, nullable=False)
    owner_phone             = Column(String, nullable=False)