from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import schemas
from app import crud
from app.utils.service_client import ServiceClient

router = APIRouter()

# Performance endpoints
# Create a new performance record
@router.post("/performance/record", response_model=schemas.UserPerformance)
async def record_performance(performance: schemas.UserPerformanceCreate, db: Session = Depends(get_db)):
    # Validate that user exists in the user-progress-service
    user_exists = await ServiceClient.validate_user_exists(performance.user_id)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate lab exists
    lab_exists = await ServiceClient.validate_lab_exists(performance.lab_type)
    if not lab_exists:
        raise HTTPException(status_code=404, detail="Lab type not found")
    
    db_performance = crud.create_performance_record(db=db, performance=performance)
    return db_performance


# Get all performance records for a lab type
@router.get("/performance/lab/{lab_type}", response_model=schemas.LabPerformance)
async def get_lab_performance(lab_type: str, db: Session = Depends(get_db)):
    # Validate lab exists
    lab_exists = await ServiceClient.validate_lab_exists(lab_type)
    if not lab_exists:
        raise HTTPException(status_code=404, detail="Lab type not found")
    
    db_lab_performance = crud.get_lab_performance(db=db, lab_type=lab_type)
    if db_lab_performance is None:
        raise HTTPException(status_code=404, detail="No records found for lab type")
    return db_lab_performance


# Get performance records by user ID
@router.get("/performance/user/{user_id}")
async def get_user_performance(user_id: str, db: Session = Depends(get_db)):
    # Validate that user exists in the user-progress-service
    user_exists = await ServiceClient.validate_user_exists(user_id)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_performance = crud.get_user_performance(db=db, user_id=user_id)
    if user_performance is None:
        return {"user_id": user_id, "records": []}
    return user_performance


# Performance record update
@router.put("/performance/record/{performance_id}", response_model=schemas.UserPerformance)
async def update_performance(
    performance_id: int,
    performance: schemas.UserPerformanceCreate,
    db: Session = Depends(get_db),
):
    # Validate that user exists in the user-progress-service
    user_exists = await ServiceClient.validate_user_exists(performance.user_id)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate lab exists
    lab_exists = await ServiceClient.validate_lab_exists(performance.lab_type)
    if not lab_exists:
        raise HTTPException(status_code=404, detail="Lab type not found")
    
    db_performance = crud.update_user_performance(db, performance_id, performance)
    if not db_performance:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return db_performance


# Performance record deletion
@router.delete("/performance/record/{performance_id}")
async def delete_performance(performance_id: int, db: Session = Depends(get_db)):
    success = crud.delete_user_performance(db, performance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return {
        "status": "success",
        "message": f"Performance record {performance_id} deleted",
    }