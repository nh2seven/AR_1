from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, Dict, List


# User schemas
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: EmailStr


class UserCreate(UserBase):
    id: Optional[str] = None  # Optional, system will generate if not provided


class UserRead(UserBase):
    id: str
    created_at: datetime
    last_active: datetime

    model_config = ConfigDict(from_attributes=True)


# Lab schemas
class LabBase(BaseModel):
    name: str
    description: str
    lab_type: str
    difficulty: str


class LabCreate(LabBase):
    id: Optional[str] = None  # Optional, system will generate if not provided


class LabRead(LabBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Performance schemas
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
    lab_name: Optional[str] = None
    lab_description: Optional[str] = None


class LabPerformance(LabPerformanceBase):
    id: int
    last_updated: datetime

    # Updated Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)
