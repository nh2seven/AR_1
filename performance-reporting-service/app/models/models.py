from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class UserPerformanceRecord(Base):
    __tablename__ = "user_performance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    lab_type = Column(String, index=True)
    completion_time = Column(Integer)
    success = Column(Boolean, default=False)
    errors = Column(JSON)
    resources_used = Column(JSON)
    timestamp = Column(DateTime(timezone=True), default=func.now())

class LabStatistics(Base):
    __tablename__ = "lab_statistics"

    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(String, unique=True, index=True)
    lab_type = Column(String, index=True)
    total_users = Column(Integer, default=0)
    avg_completion_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    common_errors = Column(JSON)
    last_updated = Column(DateTime(timezone=True), default=func.now())