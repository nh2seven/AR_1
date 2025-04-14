from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY
from sqlalchemy.sql import func
from app.database import Base

class LabAttempt(Base):
    __tablename__ = "lab_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    lab_type = Column(String)
    completion_status = Column(Boolean)
    time_spent = Column(Integer)  # seconds
    errors_encountered = Column(ARRAY(String))
    timestamp = Column(DateTime, default=func.now())
