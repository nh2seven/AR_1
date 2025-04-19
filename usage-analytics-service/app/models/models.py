from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


# Define the UsageEvent model
class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Reference to User in User Progress Service
    lab_type = Column(String, index=True)  # Reference to Lab type in User Progress Service
    event_type = Column(String)
    event_data = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), default=func.now())
