from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
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


# Define the UsageEvent model
class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    lab_type = Column(String, index=True)
    event_type = Column(String)
    event_data = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), default=func.now())
