from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict


# Lab Usage Event schemas
class LabUsageEventBase(BaseModel):
    user_id: str
    lab_type: str
    event_type: str
    event_data: Optional[Dict] = {}


# LabUsageEventCreate schema for creating a new lab usage event
class LabUsageEventCreate(LabUsageEventBase):
    pass


# LabUsageEvent schema for reading lab usage event data
class LabUsageEvent(LabUsageEventBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
