from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import (
    create_lab_attempt,
    get_attempts_by_user,
    update_lab_attempt,
    delete_lab_attempt,
    create_user,
    get_user,
    get_users,
    get_user_by_email,
    get_user_by_username,
    update_user,
    delete_user,
    create_lab,
    get_lab,
    get_lab_by_name,
    get_labs,
    get_labs_by_type,
    update_lab,
    delete_lab,
)
from app.models import schemas

router = APIRouter()


# User management endpoints
# Create a new user
@router.post("/users/", response_model=schemas.UserRead)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    return create_user(db, user)


# Get user information
@router.get("/users/", response_model=List[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = get_users(db, skip=skip, limit=limit)
    return users


# Get user by ID
@router.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: str, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Update user information
@router.put("/users/{user_id}", response_model=schemas.UserRead)
def update_user_info(user_id: str, user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump(exclude_unset=True)

    return update_user(db, user_id, user_data)


# Delete user account
@router.delete("/users/{user_id}")
def delete_user_account(user_id: str, db: Session = Depends(get_db)):
    """Delete a user account"""
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": f"User {user_id} deleted"}


# Lab management endpoints
# Create a new lab
@router.post("/labs/", response_model=schemas.LabRead)
def create_new_lab(lab: schemas.LabCreate, db: Session = Depends(get_db)):
    db_lab = get_lab_by_name(db, lab.name)
    if db_lab:
        raise HTTPException(status_code=400, detail="Lab name already exists")

    return create_lab(db, lab)


# Get all labs with pagination
@router.get("/labs/", response_model=List[schemas.LabRead])
def read_labs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    labs = get_labs(db, skip=skip, limit=limit)
    return labs


# Get labs by type
@router.get("/labs/type/{lab_type}", response_model=List[schemas.LabRead])
def read_labs_by_type(lab_type: str, db: Session = Depends(get_db)):
    labs = get_labs_by_type(db, lab_type)
    return labs


# Get lab by ID
@router.get("/labs/{lab_id}", response_model=schemas.LabRead)
def read_lab(lab_id: str, db: Session = Depends(get_db)):
    db_lab = get_lab(db, lab_id)
    if not db_lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return db_lab


# Update lab information
@router.put("/labs/{lab_id}", response_model=schemas.LabRead)
def update_lab_info(lab_id: str, lab: schemas.LabBase, db: Session = Depends(get_db)):
    db_lab = get_lab(db, lab_id)
    if not db_lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    lab_data = lab.model_dump(exclude_unset=True)

    if "name" in lab_data and lab_data["name"] != db_lab.name:
        existing_lab = get_lab_by_name(db, lab_data["name"])
        if existing_lab:
            raise HTTPException(status_code=400, detail="Lab name already exists")

    return update_lab(db, lab_id, lab_data)


# Delete lab
@router.delete("/labs/{lab_id}")
def delete_lab_record(lab_id: str, db: Session = Depends(get_db)):
    success = delete_lab(db, lab_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lab not found")
    return {"status": "success", "message": f"Lab {lab_id} deleted"}


# Lab attempts endpoints
# Create a new lab attempt
@router.post("/progress/lab-attempt", response_model=schemas.LabAttemptRead)
def record_lab_attempt(attempt: schemas.LabAttemptCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, attempt.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    labs = get_labs_by_type(db, attempt.lab_type)
    if not labs:
        raise HTTPException(status_code=404, detail=f"No labs found for type: {attempt.lab_type}")

    return create_lab_attempt(db, attempt)


# Update lab attempts
@router.put("/progress/lab-attempt/{attempt_id}", response_model=schemas.LabAttemptRead)
def update_attempt(attempt_id: int, attempt: schemas.LabAttemptCreate, db: Session = Depends(get_db)):
    db_attempt = update_lab_attempt(db, attempt_id, attempt)
    if not db_attempt:
        raise HTTPException(status_code=404, detail="Lab attempt not found")
    return db_attempt


# Delete lab attempt
@router.delete("/progress/lab-attempt/{attempt_id}")
def delete_attempt(attempt_id: int, db: Session = Depends(get_db)):
    success = delete_lab_attempt(db, attempt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lab attempt not found")
    return {"status": "success", "message": f"Lab attempt {attempt_id} deleted"}


# Get all lab attempts for a user with stats
@router.get("/progress/stats/{user_id}")
def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    attempts = get_attempts_by_user(db, user_id)
    if not attempts:
        return {
            "user_id": user_id,
            "username": db_user.username,
            "total_attempts": 0,
            "successful_attempts": 0,
            "success_rate": 0,
            "average_time_per_attempt": 0,
            "labs_attempted": [],
        }

    total_attempts = len(attempts)
    successful_attempts = len([a for a in attempts if a["completion_status"]])
    avg_time = (
        sum(a["time_spent"] for a in attempts) / total_attempts
        if total_attempts > 0
        else 0
    )

    # Group attempts by lab_type
    labs_attempted = {}
    for attempt in attempts:
        lab_type = attempt["lab_type"]
        if lab_type not in labs_attempted:
            labs_attempted[lab_type] = {
                "lab_type": lab_type,
                "lab_name": attempt["lab_name"],
                "attempts": 0,
                "successful_attempts": 0,
                "average_time": 0,
                "total_time": 0,
            }

        labs_attempted[lab_type]["attempts"] += 1
        if attempt["completion_status"]:
            labs_attempted[lab_type]["successful_attempts"] += 1
        labs_attempted[lab_type]["total_time"] += attempt["time_spent"]

    # Calculate average time for each lab
    for lab in labs_attempted.values():
        if lab["attempts"] > 0:
            lab["average_time"] = lab["total_time"] / lab["attempts"]
            lab["success_rate"] = lab["successful_attempts"] / lab["attempts"]
        del lab["total_time"]

    return {
        "user_id": user_id,
        "username": db_user.username,
        "total_attempts": total_attempts,
        "successful_attempts": successful_attempts,
        "success_rate": (
            successful_attempts / total_attempts if total_attempts > 0 else 0
        ),
        "average_time_per_attempt": avg_time,
        "labs_attempted": list(labs_attempted.values()),
    }


# Get all lab attempts for a user
@router.get("/progress/{user_id}", response_model=List[schemas.LabAttemptRead])
def get_user_progress(user_id: str, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    attempts = get_attempts_by_user(db, user_id)
    if not attempts:
        return []

    return attempts
