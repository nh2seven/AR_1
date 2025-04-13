from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from app.database import engine, Base, get_db
from app.models import models, schemas
from app import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Performance Reporting Service")

@app.post("/performance/record", response_model=schemas.UserPerformance)
async def record_performance(performance: schemas.UserPerformanceCreate, db: Session = Depends(get_db)):
    """Record performance data for a lab attempt"""
    db_performance = crud.create_performance_record(db=db, performance=performance)
    return db_performance

@app.get("/performance/lab/{lab_type}", response_model=schemas.LabPerformance)
async def get_lab_performance(lab_type: str, db: Session = Depends(get_db)):
    """Get aggregated performance metrics for a specific lab type"""
    db_lab_performance = crud.get_lab_performance(db=db, lab_type=lab_type)
    if db_lab_performance is None:
        raise HTTPException(status_code=404, detail="No records found for lab type")
    return db_lab_performance

@app.get("/performance/user/{user_id}")
async def get_user_performance(user_id: str, db: Session = Depends(get_db)):
    """Get detailed performance metrics for a specific user across all labs"""
    user_performance = crud.get_user_performance(db=db, user_id=user_id)
    if user_performance is None:
        raise HTTPException(status_code=404, detail="No records found for user")
    return user_performance