from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import models, schemas
import uuid


# User CRUD operations
# Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    user_id = user.id if user.id else str(uuid.uuid4())

    db_user = models.User(
        id=user_id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        created_at=datetime.now(),
        last_active=datetime.now(),
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
        db_user.last_active = datetime.now()
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
        created_at=datetime.now(),
        updated_at=datetime.now(),
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
        db_lab.updated_at = datetime.now()
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


# Event CRUD operations
# Create a new lab usage event
def create_event(db: Session, event: schemas.LabUsageEventCreate):
    db_event = models.UsageEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# Get event by ID
def get_lab_events(db: Session, lab_type: str, days: int = 7):
    cutoff_date = datetime.now() - timedelta(days=days)
    return (
        db.query(models.UsageEvent)
        .filter(
            models.UsageEvent.lab_type == lab_type,
            models.UsageEvent.timestamp >= cutoff_date,
        )
        .all()
    )


# Get all events with pagination
def get_recent_events(db: Session, days: int = 30):
    cutoff_date = datetime.now() - timedelta(days=days)
    return (
        db.query(models.UsageEvent)
        .filter(models.UsageEvent.timestamp >= cutoff_date)
        .all()
    )


# Update event information
def update_event(db: Session, event_id: int, event: schemas.LabUsageEventCreate):
    db_event = (db.query(models.UsageEvent).filter(models.UsageEvent.id == event_id).first())
    if db_event:
        for key, value in event.model_dump().items():
            setattr(db_event, key, value)
        db.commit()
        db.refresh(db_event)
    return db_event


# Delete an event by ID
def delete_event(db: Session, event_id: int):
    db_event = (db.query(models.UsageEvent).filter(models.UsageEvent.id == event_id).first())
    if db_event:
        db.delete(db_event)
        db.commit()
        return True
    return False
