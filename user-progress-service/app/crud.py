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

def update_lab_attempt(db: Session, attempt_id: int, attempt: schemas.LabAttemptCreate):
    db_attempt = db.query(models.LabAttempt).filter(models.LabAttempt.id == attempt_id).first()
    if db_attempt:
        for key, value in attempt.model_dump().items():
            setattr(db_attempt, key, value)
        db.commit()
        db.refresh(db_attempt)
    return db_attempt

def delete_lab_attempt(db: Session, attempt_id: int):
    db_attempt = db.query(models.LabAttempt).filter(models.LabAttempt.id == attempt_id).first()
    if db_attempt:
        db.delete(db_attempt)
        db.commit()
        return True
    return False
