from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import models, schemas

# Event CRUD operations
# Create a new lab usage event
def create_event(db: Session, event: schemas.LabUsageEventCreate):
    db_event = models.UsageEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# Get events for a specific lab type
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

# Get all recent events 
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
