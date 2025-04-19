from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import List, Optional


# User schemas
# Base schema for user data
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: EmailStr


# Optional fields for user creation
class UserCreate(UserBase):
    id: Optional[str] = None


# UserRead schema with additional fields
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


# Optional fields for lab creation
class LabCreate(LabBase):
    id: Optional[str] = None


# LabRead schema with additional fields
class LabRead(LabBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Lab Attempt schemas
class LabAttemptBase(BaseModel):
    user_id: str
    lab_type: str
    completion_status: bool
    time_spent: int
    errors_encountered: Optional[List[str]] = []


# LabAttemptCreate schema with additional fields; to be implemented if needed
class LabAttemptCreate(LabAttemptBase):
    pass


# LabAttemptRead schema with additional fields
class LabAttemptRead(LabAttemptBase):
    id: int
    timestamp: datetime
    lab_name: Optional[str] = None
    lab_description: Optional[str] = None
    lab_difficulty: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
