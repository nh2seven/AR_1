from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from app.database import get_db
from app.models import schemas
from app import crud

router = APIRouter()

# User management endpoints
@router.post("/users/", response_model=schemas.UserRead)
async def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user with same email already exists
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username is taken
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.create_user(db, user)

@router.get("/users/", response_model=List[schemas.UserRead])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.UserRead)
async def read_user(user_id: str, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=schemas.UserRead)
async def update_user_info(user_id: str, user: schemas.UserBase, db: Session = Depends(get_db)):
    """Update user information"""
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert Pydantic model to dict excluding unset values
    user_data = user.model_dump(exclude_unset=True)
    
    return crud.update_user(db, user_id, user_data)

@router.delete("/users/{user_id}")
async def delete_user_account(user_id: str, db: Session = Depends(get_db)):
    """Delete a user account"""
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": f"User {user_id} deleted"}

# Lab management endpoints
@router.post("/labs/", response_model=schemas.LabRead)
async def create_new_lab(lab: schemas.LabCreate, db: Session = Depends(get_db)):
    """Create a new lab"""
    # Check if lab with same name already exists
    db_lab = crud.get_lab_by_name(db, lab.name)
    if db_lab:
        raise HTTPException(status_code=400, detail="Lab name already exists")
    
    return crud.create_lab(db, lab)

@router.get("/labs/", response_model=List[schemas.LabRead])
async def read_labs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all labs with pagination"""
    labs = crud.get_labs(db, skip=skip, limit=limit)
    return labs

@router.get("/labs/{lab_id}", response_model=schemas.LabRead)
async def read_lab(lab_id: str, db: Session = Depends(get_db)):
    """Get a specific lab by ID"""
    db_lab = crud.get_lab(db, lab_id)
    if not db_lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return db_lab

@router.get("/labs/type/{lab_type}", response_model=List[schemas.LabRead])
async def read_labs_by_type(lab_type: str, db: Session = Depends(get_db)):
    """Get all labs of a specific type"""
    labs = crud.get_labs_by_type(db, lab_type)
    return labs

@router.put("/labs/{lab_id}", response_model=schemas.LabRead)
async def update_lab_info(lab_id: str, lab: schemas.LabBase, db: Session = Depends(get_db)):
    """Update lab information"""
    db_lab = crud.get_lab(db, lab_id)
    if not db_lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    
    # Convert Pydantic model to dict excluding unset values
    lab_data = lab.model_dump(exclude_unset=True)
    
    # If name is being updated, check it's not taken
    if "name" in lab_data and lab_data["name"] != db_lab.name:
        existing_lab = crud.get_lab_by_name(db, lab_data["name"])
        if existing_lab:
            raise HTTPException(status_code=400, detail="Lab name already exists")
    
    return crud.update_lab(db, lab_id, lab_data)

@router.delete("/labs/{lab_id}")
async def delete_lab_record(lab_id: str, db: Session = Depends(get_db)):
    """Delete a lab"""
    success = crud.delete_lab(db, lab_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lab not found")
    return {"status": "success", "message": f"Lab {lab_id} deleted"}

# Analytics events endpoints
@router.post("/analytics/event", response_model=schemas.LabUsageEvent)
async def record_event(event: schemas.LabUsageEventCreate, db: Session = Depends(get_db)):
    # Verify user exists
    db_user = crud.get_user(db, event.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.create_event(db=db, event=event)

@router.get("/analytics/usage/lab/{lab_type}")
async def get_lab_usage(lab_type: str, days: int = 7, db: Session = Depends(get_db)):
    events = crud.get_lab_events(db, lab_type, days)
    if not events:
        raise HTTPException(status_code=404, detail="No usage data found for lab type")
    
    unique_users = len(set(e.user_id for e in events))
    event_counts = {}
    sessions = {}
    
    for event in events:
        event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        if event.event_type in ['start', 'complete']:
            if event.user_id not in sessions:
                sessions[event.user_id] = []
            sessions[event.user_id].append(event)
    
    total_session_time = timedelta()
    session_count = 0
    for user_sessions in sessions.values():
        user_sessions.sort(key=lambda x: x.timestamp)
        for i in range(0, len(user_sessions) - 1, 2):
            if i + 1 < len(user_sessions):
                session_time = user_sessions[i + 1].timestamp - user_sessions[i].timestamp
                total_session_time += session_time
                session_count += 1
    
    avg_session_time = (total_session_time.total_seconds() / session_count) if session_count > 0 else 0
    
    return {
        "lab_type": lab_type,
        "time_period_days": days,
        "unique_users": unique_users,
        "total_events": len(events),
        "event_distribution": event_counts,
        "average_session_time_seconds": avg_session_time
    }

@router.get("/analytics/trends")
async def get_usage_trends(days: int = 30, db: Session = Depends(get_db)):
    events = crud.get_recent_events(db, days)
    
    lab_usage = {}
    for event in events:
        if event.lab_type not in lab_usage:
            lab_usage[event.lab_type] = {
                "total_events": 0,
                "unique_users": set(),
                "errors": 0
            }
        lab_usage[event.lab_type]["total_events"] += 1
        lab_usage[event.lab_type]["unique_users"].add(event.user_id)
        if event.event_type == "error":
            lab_usage[event.lab_type]["errors"] += 1
    
    # Convert sets to counts for JSON serialization
    for lab in lab_usage.values():
        lab["unique_users"] = len(lab["unique_users"])
    
    return {
        "time_period_days": days,
        "total_events": len(events),
        "lab_usage": lab_usage
    }

@router.put("/analytics/event/{event_id}", response_model=schemas.LabUsageEvent)
async def update_event(event_id: int, event: schemas.LabUsageEventCreate, db: Session = Depends(get_db)):
    # Verify user exists
    db_user = crud.get_user(db, event.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db_event = crud.update_event(db, event_id, event)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@router.delete("/analytics/event/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    success = crud.delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"status": "success", "message": f"Event {event_id} deleted"}
