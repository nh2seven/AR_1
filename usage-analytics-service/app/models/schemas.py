from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, Dict


# User schemas
# Base schema for user data
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: EmailStr


# UserCreate schema for creating a new user
class UserCreate(UserBase):
    id: Optional[str] = None


# UserRead schema for reading user data
class UserRead(UserBase):
    id: str
    created_at: datetime
    last_active: datetime

    model_config = ConfigDict(from_attributes=True)


# Lab schemas
# Base schema for lab data
class LabBase(BaseModel):
    name: str
    description: str
    lab_type: str
    difficulty: str


# LabCreate schema for creating a new lab
class LabCreate(LabBase):
    id: Optional[str] = None


# LabRead schema for reading lab data
class LabRead(LabBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Lab Usage Event schemas
# Base schema for lab usage events
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
