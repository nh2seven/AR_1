from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


# Define the UserPerformanceRecord model
class UserPerformanceRecord(Base):
    __tablename__ = "user_performance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Reference to User in User Progress Service
    lab_type = Column(String, index=True)  # Reference to Lab type in User Progress Service
    completion_time = Column(Integer)
    success = Column(Boolean, default=False)
    errors = Column(JSON)
    resources_used = Column(JSON)
    timestamp = Column(DateTime(timezone=True), default=func.now())


# Define the LabStatistics model
class LabStatistics(Base):
    __tablename__ = "lab_statistics"

    id = Column(Integer, primary_key=True, index=True)
    lab_type = Column(String, index=True)  # Reference to Lab type in User Progress Service
    total_users = Column(Integer, default=0)
    avg_completion_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    common_errors = Column(JSON)
    last_updated = Column(DateTime(timezone=True), default=func.now())
