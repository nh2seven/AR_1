from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Dict, List

app = FastAPI(title="Usage Analytics Service")

class LabUsageEvent(BaseModel):
    user_id: str
    lab_type: str
    event_type: str  # start, complete, error, resource_access
    event_data: Optional[Dict] = {}
    timestamp: datetime = datetime.now()

# In-memory storage for demo purposes
usage_events = []

@app.post("/analytics/event")
async def record_event(event: LabUsageEvent):
    usage_events.append(event)
    return {"status": "success", "message": "Event recorded"}

@app.get("/analytics/usage/lab/{lab_type}")
async def get_lab_usage(lab_type: str, days: Optional[int] = 7):
    cutoff_date = datetime.now() - timedelta(days=days)
    relevant_events = [e for e in usage_events 
                      if e.lab_type == lab_type and e.timestamp >= cutoff_date]
    
    if not relevant_events:
        raise HTTPException(status_code=404, detail="No usage data found for lab type")
    
    # Analyze usage patterns
    unique_users = len(set(e.user_id for e in relevant_events))
    event_counts = {}
    for event in relevant_events:
        event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
    
    # Calculate average session time
    sessions = {}
    for event in relevant_events:
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
    
    avg_session_time = (total_session_time / session_count).total_seconds() if session_count > 0 else 0
    
    return {
        "lab_type": lab_type,
        "time_period_days": days,
        "unique_users": unique_users,
        "total_events": len(relevant_events),
        "event_distribution": event_counts,
        "average_session_time_seconds": avg_session_time
    }

@app.get("/analytics/trends")
async def get_usage_trends(days: Optional[int] = 30):
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_events = [e for e in usage_events if e.timestamp >= cutoff_date]
    
    # Analyze trends by lab type
    lab_usage = {}
    for event in recent_events:
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
        "total_events": len(recent_events),
        "lab_usage": lab_usage
    }