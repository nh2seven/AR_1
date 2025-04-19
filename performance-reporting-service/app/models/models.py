from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, default=func.now())


# Define the Lab model
class Lab(Base):
    __tablename__ = "labs"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    lab_type = Column(String, index=True)
    difficulty = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Define the UserPerformanceRecord model
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


# Define the LabStatistics model
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
