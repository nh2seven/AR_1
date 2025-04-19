from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import engine, Base, get_db
from app.models import schemas
from app import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Performance Reporting Service")


# User management endpoints
# Create a new user
@app.post("/users/", response_model=schemas.UserRead)
async def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    return crud.create_user(db, user)


# Get all users
@app.get("/users/", response_model=List[schemas.UserRead])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# Get user by ID
@app.get("/users/{user_id}", response_model=schemas.UserRead)
async def read_user(user_id: str, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Get user by username
@app.put("/users/{user_id}", response_model=schemas.UserRead)
async def update_user_info(user_id: str, user: schemas.UserBase, db: Session = Depends(get_db)):
    """Update user information"""
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump(exclude_unset=True)

    return crud.update_user(db, user_id, user_data)


# User account deletion
@app.delete("/users/{user_id}")
async def delete_user_account(user_id: str, db: Session = Depends(get_db)):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "message": f"User {user_id} deleted"}


# Lab management endpoints
# Create a new lab
@app.post("/labs/", response_model=schemas.LabRead)
async def create_new_lab(lab: schemas.LabCreate, db: Session = Depends(get_db)):
    db_lab = crud.get_lab_by_name(db, lab.name)
    if db_lab:
        raise HTTPException(status_code=400, detail="Lab name already exists")

    return crud.create_lab(db, lab)


# Get all labs
@app.get("/labs/", response_model=List[schemas.LabRead])
async def read_labs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all labs with pagination"""
    labs = crud.get_labs(db, skip=skip, limit=limit)
    return labs


# Get lab by ID
@app.get("/labs/{lab_id}", response_model=schemas.LabRead)
async def read_lab(lab_id: str, db: Session = Depends(get_db)):
    """Get a specific lab by ID"""
    db_lab = crud.get_lab(db, lab_id)
    if not db_lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return db_lab


# Get labs by type
@app.get("/labs/type/{lab_type}", response_model=List[schemas.LabRead])
async def read_labs_by_type(lab_type: str, db: Session = Depends(get_db)):
    """Get all labs of a specific type"""
    labs = crud.get_labs_by_type(db, lab_type)
    return labs


# Update lab information
@app.put("/labs/{lab_id}", response_model=schemas.LabRead)
async def update_lab_info(lab_id: str, lab: schemas.LabBase, db: Session = Depends(get_db)):
    db_lab = crud.get_lab(db, lab_id)
    if not db_lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    lab_data = lab.model_dump(exclude_unset=True)

    if "name" in lab_data and lab_data["name"] != db_lab.name:
        existing_lab = crud.get_lab_by_name(db, lab_data["name"])
        if existing_lab:
            raise HTTPException(status_code=400, detail="Lab name already exists")

    return crud.update_lab(db, lab_id, lab_data)


# Delete lab
@app.delete("/labs/{lab_id}")
async def delete_lab_record(lab_id: str, db: Session = Depends(get_db)):
    success = crud.delete_lab(db, lab_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lab not found")
    return {"status": "success", "message": f"Lab {lab_id} deleted"}


# Performance endpoints
# Create a new performance record
@app.post("/performance/record", response_model=schemas.UserPerformance)
async def record_performance(performance: schemas.UserPerformanceCreate, db: Session = Depends(get_db)):
    db_performance = crud.create_performance_record(db=db, performance=performance)
    if not db_performance:
        raise HTTPException(status_code=404, detail="User not found")
    return db_performance


# Get all performance records
@app.get("/performance/lab/{lab_type}", response_model=schemas.LabPerformance)
async def get_lab_performance(lab_type: str, db: Session = Depends(get_db)):
    db_lab_performance = crud.get_lab_performance(db=db, lab_type=lab_type)
    if db_lab_performance is None:
        raise HTTPException(status_code=404, detail="No records found for lab type")
    return db_lab_performance


# Get performance records by user ID
@app.get("/performance/user/{user_id}")
async def get_user_performance(user_id: str, db: Session = Depends(get_db)):
    user_performance = crud.get_user_performance(db=db, user_id=user_id)
    if user_performance is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_performance


# Performance record update
@app.put("/performance/record/{performance_id}", response_model=schemas.UserPerformance)
async def update_performance(
    performance_id: int,
    performance: schemas.UserPerformanceCreate,
    db: Session = Depends(get_db),
):
    db_performance = crud.update_user_performance(db, performance_id, performance)
    if not db_performance:
        raise HTTPException(status_code=404, detail="Performance record not found or user not found")
    return db_performance


# Performance record deletion
@app.delete("/performance/record/{performance_id}")
async def delete_performance(performance_id: int, db: Session = Depends(get_db)):
    success = crud.delete_user_performance(db, performance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return {
        "status": "success",
        "message": f"Performance record {performance_id} deleted",
    }
