from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

app = FastAPI(title="User Progress Tracking Service")

class LabAttempt(BaseModel):
    user_id: str
    lab_type: str
    completion_status: bool
    time_spent: int  # in seconds
    errors_encountered: Optional[List[str]] = []
    timestamp: datetime = datetime.now()

# In-memory storage for demo purposes
# In production, use a proper database
progress_records = []

@app.post("/progress/lab-attempt")
async def record_lab_attempt(attempt: LabAttempt):
    progress_records.append(attempt)
    return {"status": "success", "message": "Lab attempt recorded"}

@app.get("/progress/{user_id}")
async def get_user_progress(user_id: str):
    user_attempts = [attempt for attempt in progress_records if attempt.user_id == user_id]
    if not user_attempts:
        raise HTTPException(status_code=404, detail="No records found for user")
    return user_attempts

@app.get("/progress/stats/{user_id}")
async def get_user_stats(user_id: str):
    user_attempts = [attempt for attempt in progress_records if attempt.user_id == user_id]
    if not user_attempts:
        raise HTTPException(status_code=404, detail="No records found for user")
    
    total_attempts = len(user_attempts)
    successful_attempts = len([a for a in user_attempts if a.completion_status])
    avg_time = sum(a.time_spent for a in user_attempts) / total_attempts if total_attempts > 0 else 0
    
    return {
        "total_attempts": total_attempts,
        "successful_attempts": successful_attempts,
        "success_rate": successful_attempts / total_attempts if total_attempts > 0 else 0,
        "average_time_per_attempt": avg_time
    }