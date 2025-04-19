from sqlalchemy.orm import Session
from app.models import models, schemas
from sqlalchemy.sql import func
import uuid
from datetime import datetime


# User CRUD operations
# Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    user_id = user.id if user.id else str(uuid.uuid4())

    db_user = models.User(
        id=user_id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        created_at=func.now(),
        last_active=func.now(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Get user by ID, email, or username
def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


# Get all users with pagination
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


# Update user information
def update_user(db: Session, user_id: str, user_data: dict):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for key, value in user_data.items():
            setattr(db_user, key, value)
        db_user.last_active = func.now()
        db.commit()
        db.refresh(db_user)
    return db_user


# Delete a user by ID
def delete_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# Lab CRUD operations
# Create a new lab
def create_lab(db: Session, lab: schemas.LabCreate):
    lab_id = lab.id if lab.id else str(uuid.uuid4())

    db_lab = models.Lab(
        id=lab_id,
        name=lab.name,
        description=lab.description,
        lab_type=lab.lab_type,
        difficulty=lab.difficulty,
        created_at=func.now(),
        updated_at=func.now(),
    )
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    return db_lab


# Get lab by ID, name, or type
def get_lab(db: Session, lab_id: str):
    return db.query(models.Lab).filter(models.Lab.id == lab_id).first()


def get_lab_by_name(db: Session, name: str):
    return db.query(models.Lab).filter(models.Lab.name == name).first()


def get_labs_by_type(db: Session, lab_type: str):
    return db.query(models.Lab).filter(models.Lab.lab_type == lab_type).all()


# Get all labs with pagination
def get_labs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Lab).offset(skip).limit(limit).all()


# Update lab information
def update_lab(db: Session, lab_id: str, lab_data: dict):
    db_lab = db.query(models.Lab).filter(models.Lab.id == lab_id).first()
    if db_lab:
        for key, value in lab_data.items():
            setattr(db_lab, key, value)
        db_lab.updated_at = func.now()
        db.commit()
        db.refresh(db_lab)
    return db_lab


# Delete a lab by ID
def delete_lab(db: Session, lab_id: str):
    db_lab = db.query(models.Lab).filter(models.Lab.id == lab_id).first()
    if db_lab:
        db.delete(db_lab)
        db.commit()
        return True
    return False


# Lab Attempt CRUD operations
# Create a new lab attempt
def create_lab_attempt(db: Session, attempt: schemas.LabAttemptCreate):
    db_attempt = models.LabAttempt(**attempt.model_dump(), timestamp=func.now())
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt


# Get lab attempt by user
def get_attempts_by_user(db: Session, user_id: str):
    attempts = (db.query(models.LabAttempt).filter(models.LabAttempt.user_id == user_id).all())

    # Enrich attempts with lab information
    enriched_attempts = []
    for attempt in attempts:
        # Get the lab details for this attempt
        lab = (
            db.query(models.Lab).filter(models.Lab.lab_type == attempt.lab_type).first()
        )

        # Create a copy of the attempt with additional attributes
        attempt_dict = {
            c.name: getattr(attempt, c.name) for c in attempt.__table__.columns
        }
        if lab:
            attempt_dict["lab_name"] = lab.name
            attempt_dict["lab_description"] = lab.description
            attempt_dict["lab_difficulty"] = lab.difficulty
        else:
            attempt_dict["lab_name"] = (
                attempt.lab_type
            )  # Fallback to lab_type if lab not found
            attempt_dict["lab_description"] = "No description available"
            attempt_dict["lab_difficulty"] = "unknown"

        enriched_attempts.append(attempt_dict)

    return enriched_attempts


# Update lab attempt information
def update_lab_attempt(db: Session, attempt_id: int, attempt: schemas.LabAttemptCreate):
    db_attempt = (db.query(models.LabAttempt).filter(models.LabAttempt.id == attempt_id).first())
    if db_attempt:
        for key, value in attempt.model_dump().items():
            setattr(db_attempt, key, value)
        db.commit()
        db.refresh(db_attempt)
    return db_attempt


# Delete a lab attempt by ID
def delete_lab_attempt(db: Session, attempt_id: int):
    db_attempt = (db.query(models.LabAttempt).filter(models.LabAttempt.id == attempt_id).first())
    if db_attempt:
        db.delete(db_attempt)
        db.commit()
        return True
    return False
