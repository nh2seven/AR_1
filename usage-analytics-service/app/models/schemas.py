from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict

class LabUsageEventBase(BaseModel):
    user_id: str
    lab_type: str
    event_type: str
    event_data: Optional[Dict] = {}

class LabUsageEventCreate(LabUsageEventBase):
    pass

class LabUsageEvent(LabUsageEventBase):
    id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)