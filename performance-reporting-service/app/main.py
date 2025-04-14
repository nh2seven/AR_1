from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import schemas
from app import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Performance Reporting Service")


@app.post("/performance/record", response_model=schemas.UserPerformance)
async def record_performance(performance: schemas.UserPerformanceCreate, db: Session = Depends(get_db)):
    db_performance = crud.create_performance_record(db=db, performance=performance)
    return db_performance


@app.get("/performance/lab/{lab_type}", response_model=schemas.LabPerformance)
async def get_lab_performance(lab_type: str, db: Session = Depends(get_db)):
    db_lab_performance = crud.get_lab_performance(db=db, lab_type=lab_type)
    if db_lab_performance is None:
        raise HTTPException(status_code=404, detail="No records found for lab type")
    return db_lab_performance


@app.get("/performance/user/{user_id}")
async def get_user_performance(user_id: str, db: Session = Depends(get_db)):
    user_performance = crud.get_user_performance(db=db, user_id=user_id)
    if user_performance is None:
        raise HTTPException(status_code=404, detail="No records found for user")
    return user_performance


@app.put("/performance/record/{performance_id}", response_model=schemas.UserPerformance)
async def update_performance(
    performance_id: int,
    performance: schemas.UserPerformanceCreate,
    db: Session = Depends(get_db),
):
    """Update an existing performance record"""
    db_performance = crud.update_user_performance(db, performance_id, performance)
    if not db_performance:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return db_performance


@app.delete("/performance/record/{performance_id}")
async def delete_performance(performance_id: int, db: Session = Depends(get_db)):
    success = crud.delete_user_performance(db, performance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return {
        "status": "success",
        "message": f"Performance record {performance_id} deleted",
    }
