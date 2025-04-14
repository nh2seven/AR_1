from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import schemas
from app import crud

router = APIRouter()

@router.post("/analytics/event", response_model=schemas.LabUsageEvent)
async def record_event(event: schemas.LabUsageEventCreate, db: Session = Depends(get_db)):
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
