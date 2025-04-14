from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import create_lab_attempt, get_attempts_by_user, update_lab_attempt, delete_lab_attempt
from app.models import schemas

router = APIRouter()


@router.post("/progress/lab-attempt", response_model=schemas.LabAttemptRead)
def record_lab_attempt(attempt: schemas.LabAttemptCreate, db: Session = Depends(get_db)):
    return create_lab_attempt(db, attempt)


@router.get("/progress/{user_id}", response_model=List[schemas.LabAttemptRead])
def get_user_progress(user_id: str, db: Session = Depends(get_db)):
    attempts = get_attempts_by_user(db, user_id)
    if not attempts:
        raise HTTPException(status_code=404, detail="No records found for user")
    return attempts


@router.get("/progress/stats/{user_id}")
def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    attempts = get_attempts_by_user(db, user_id)
    if not attempts:
        raise HTTPException(status_code=404, detail="No records found for user")

    total_attempts = len(attempts)
    successful_attempts = len([a for a in attempts if a.completion_status])
    avg_time = (
        sum(a.time_spent for a in attempts) / total_attempts
        if total_attempts > 0
        else 0
    )

    return {
        "total_attempts": total_attempts,
        "successful_attempts": successful_attempts,
        "success_rate": successful_attempts / total_attempts,
        "average_time_per_attempt": avg_time,
    }


@router.put("/progress/lab-attempt/{attempt_id}", response_model=schemas.LabAttemptRead)
def update_attempt(attempt_id: int, attempt: schemas.LabAttemptCreate, db: Session = Depends(get_db)):
    """Update an existing lab attempt"""
    db_attempt = update_lab_attempt(db, attempt_id, attempt)
    if not db_attempt:
        raise HTTPException(status_code=404, detail="Lab attempt not found")
    return db_attempt


@router.delete("/progress/lab-attempt/{attempt_id}")
def delete_attempt(attempt_id: int, db: Session = Depends(get_db)):
    """Delete a lab attempt"""
    success = delete_lab_attempt(db, attempt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lab attempt not found")
    return {"status": "success", "message": f"Lab attempt {attempt_id} deleted"}
