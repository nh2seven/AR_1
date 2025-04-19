from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from collections import Counter
from app.models import models, schemas
import uuid
from datetime import datetime


# User CRUD operations
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


# Get user by ID
def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


# Get user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# Get user by username
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


# Delete user by ID
def delete_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# Lab CRUD operations
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


# Get lab by ID
def get_lab(db: Session, lab_id: str):
    return db.query(models.Lab).filter(models.Lab.id == lab_id).first()


# Get lab by name
def get_lab_by_name(db: Session, name: str):
    return db.query(models.Lab).filter(models.Lab.name == name).first()


# Get labs by type
def get_labs_by_type(db: Session, lab_type: str):
    return db.query(models.Lab).filter(models.Lab.lab_type == lab_type).all()


# Get all labs with pagination
def get_labs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Lab).offset(skip).limit(limit).all()


# Get lab performance statistics
def update_lab(db: Session, lab_id: str, lab_data: dict):
    db_lab = db.query(models.Lab).filter(models.Lab.id == lab_id).first()
    if db_lab:
        for key, value in lab_data.items():
            setattr(db_lab, key, value)
        db_lab.updated_at = datetime.now()
        db.commit()
        db.refresh(db_lab)
    return db_lab


# Delete lab by ID
def delete_lab(db: Session, lab_id: str):
    db_lab = db.query(models.Lab).filter(models.Lab.id == lab_id).first()
    if db_lab:
        db.delete(db_lab)
        db.commit()
        return True
    return False


# Performance record CRUD operations
def create_performance_record(db: Session, performance: schemas.UserPerformanceCreate):
    user = get_user(db, performance.user_id)
    if not user:
        return None

    db_performance = models.UserPerformanceRecord(
        user_id=performance.user_id,
        lab_type=performance.lab_type,
        completion_time=performance.completion_time,
        success=performance.success,
        errors=performance.errors,
        resources_used=performance.resources_used,
    )
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)

    # Update user's last active timestamp
    user.last_active = datetime.now()
    db.commit()

    return db_performance


# Get lab performance statistics
def get_lab_performance(db: Session, lab_type: str):
    records = (
        db.query(models.UserPerformanceRecord)
        .filter(models.UserPerformanceRecord.lab_type == lab_type)
        .all()
    )

    if not records:
        return None

    # Get the lab details for this lab type
    lab = db.query(models.Lab).filter(models.Lab.lab_type == lab_type).first()
    lab_name = lab.name if lab else lab_type
    lab_description = lab.description if lab else "No description available"

    unique_users = len(set(r.user_id for r in records))
    total_records = len(records)
    avg_time = sum(r.completion_time for r in records) / total_records
    success_count = len([r for r in records if r.success])
    success_rate = success_count / total_records

    # Aggregate common errors
    all_errors = [error for r in records for error in r.errors]
    error_counter = Counter(all_errors)
    common_errors = [error for error, _ in error_counter.most_common(5)]

    # Update or create lab statistics
    db_stats = (
        db.query(models.LabStatistics)
        .filter(models.LabStatistics.lab_id == lab_type)
        .first()
    )

    if db_stats:
        db_stats.total_users = unique_users
        db_stats.avg_completion_time = avg_time
        db_stats.success_rate = success_rate
        db_stats.common_errors = common_errors
        db_stats.last_updated = func.now()
    else:
        db_stats = models.LabStatistics(
            lab_id=lab_type,
            lab_type=lab_type,
            total_users=unique_users,
            avg_completion_time=avg_time,
            success_rate=success_rate,
            common_errors=common_errors,
        )
        db.add(db_stats)

    db.commit()
    db.refresh(db_stats)

    # Add lab name and description to the statistics object before returning
    db_stats_dict = {c.name: getattr(db_stats, c.name) for c in db_stats.__table__.columns}
    db_stats_dict["lab_name"] = lab_name
    db_stats_dict["lab_description"] = lab_description

    return db_stats_dict


# Get user performance record
def get_user_performance(db: Session, user_id: str):
    user = get_user(db, user_id)
    if not user:
        return None

    records = (
        db.query(models.UserPerformanceRecord)
        .filter(models.UserPerformanceRecord.user_id == user_id)
        .all()
    )

    # Return basic user info but no performance data
    if not records:
        return {"user_id": user_id, "username": user.username, "performance_by_lab": {}}

    # Group records by lab_type
    performance_by_lab = {}
    for record in records:
        if record.lab_type not in performance_by_lab:
            performance_by_lab[record.lab_type] = []
        performance_by_lab[record.lab_type].append(record)

    # Get lab details for each lab type
    lab_details = {}
    for lab_type in performance_by_lab.keys():
        lab = db.query(models.Lab).filter(models.Lab.lab_type == lab_type).first()
        if lab:
            lab_details[lab_type] = {
                "name": lab.name,
                "description": lab.description,
                "difficulty": lab.difficulty,
            }
        else:
            lab_details[lab_type] = {
                "name": lab_type,
                "description": "No description available",
                "difficulty": "unknown",
            }

    # Build enhanced result with lab information
    result = {
        "user_id": user_id,
        "username": user.username,
        "performance_by_lab": {
            lab_type: {
                "lab_name": lab_details[lab_type]["name"],
                "lab_description": lab_details[lab_type]["description"],
                "lab_difficulty": lab_details[lab_type]["difficulty"],
                "attempts": len(lab_records),
                "success_rate": len([r for r in lab_records if r.success])
                / len(lab_records),
                "avg_completion_time": sum(r.completion_time for r in lab_records)
                / len(lab_records),
                "total_time_spent": sum(r.completion_time for r in lab_records),
                "last_attempt": max(r.timestamp for r in lab_records).isoformat(),
            }
            for lab_type, lab_records in performance_by_lab.items()
        },
    }

    return result


# Update user performance record
def update_user_performance(db: Session, performance_id: int, performance: schemas.UserPerformanceCreate):
    user = get_user(db, performance.user_id)
    if not user:
        return None

    db_performance = (
        db.query(models.UserPerformanceRecord)
        .filter(models.UserPerformanceRecord.id == performance_id)
        .first()
    )
    if db_performance:
        for key, value in performance.model_dump().items():
            setattr(db_performance, key, value)
        db.commit()
        db.refresh(db_performance)
    return db_performance


def delete_user_performance(db: Session, performance_id: int):
    db_performance = (
        db.query(models.UserPerformanceRecord)
        .filter(models.UserPerformanceRecord.id == performance_id)
        .first()
    )
    if db_performance:
        db.delete(db_performance)
        db.commit()
        return True
    return False
