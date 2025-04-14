from sqlalchemy.orm import Session
from app.models import models, schemas
from sqlalchemy.sql import func

def create_lab_attempt(db: Session, attempt: schemas.LabAttemptCreate):
    db_attempt = models.LabAttempt(**attempt.model_dump(), timestamp=func.now())
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

def get_attempts_by_user(db: Session, user_id: str):
    return db.query(models.LabAttempt).filter(models.LabAttempt.user_id == user_id).all()
