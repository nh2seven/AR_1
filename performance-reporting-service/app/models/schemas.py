from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, List

class UserPerformanceBase(BaseModel):
    user_id: str
    lab_type: str
    completion_time: int
    success: bool
    errors: Optional[List[str]] = []
    resources_used: Optional[Dict[str, int]] = {}

class UserPerformanceCreate(UserPerformanceBase):
    pass

class UserPerformance(UserPerformanceBase):
    id: int
    timestamp: datetime
    
    # Updated Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)

class LabPerformanceBase(BaseModel):
    lab_id: str
    lab_type: str
    total_users: int
    avg_completion_time: float
    success_rate: float
    common_errors: List[str]

class LabPerformance(LabPerformanceBase):
    id: int
    last_updated: datetime
    
    # Updated Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)