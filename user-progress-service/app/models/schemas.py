from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class LabAttemptBase(BaseModel):
    user_id: str
    lab_type: str
    completion_status: bool
    time_spent: int
    errors_encountered: Optional[List[str]] = []

class LabAttemptCreate(LabAttemptBase):
    pass

class LabAttemptRead(LabAttemptBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
