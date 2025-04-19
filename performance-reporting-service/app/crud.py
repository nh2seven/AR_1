from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from collections import Counter
from app.models import models, schemas
import uuid
from datetime import datetime


# Performance record CRUD operations
def create_performance_record(db: Session, performance: schemas.UserPerformanceCreate):
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
        .filter(models.LabStatistics.lab_type == lab_type)
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
            lab_type=lab_type,
            total_users=unique_users,
            avg_completion_time=avg_time,
            success_rate=success_rate,
            common_errors=common_errors,
        )
        db.add(db_stats)

    db.commit()
    db.refresh(db_stats)

    # Create a dictionary representation of the statistics
    db_stats_dict = {c.name: getattr(db_stats, c.name) for c in db_stats.__table__.columns}
    db_stats_dict["lab_name"] = lab_type  # Use lab_type as a fallback
    db_stats_dict["lab_description"] = "Information from Performance Reporting Service"

    return db_stats_dict


# Get user performance record
def get_user_performance(db: Session, user_id: str):
    records = (
        db.query(models.UserPerformanceRecord)
        .filter(models.UserPerformanceRecord.user_id == user_id)
        .all()
    )

    # Return basic user info but no performance data
    if not records:
        return {"user_id": user_id, "records": []}

    # Group records by lab_type
    performance_by_lab = {}
    for record in records:
        if record.lab_type not in performance_by_lab:
            performance_by_lab[record.lab_type] = []
        performance_by_lab[record.lab_type].append(record)

    # Build result
    result = {
        "user_id": user_id,
        "performance_by_lab": {
            lab_type: {
                "lab_type": lab_type,
                "attempts": len(lab_records),
                "success_rate": len([r for r in lab_records if r.success]) / len(lab_records),
                "avg_completion_time": sum(r.completion_time for r in lab_records) / len(lab_records),
                "total_time_spent": sum(r.completion_time for r in lab_records),
                "last_attempt": max(r.timestamp for r in lab_records).isoformat(),
            }
            for lab_type, lab_records in performance_by_lab.items()
        },
    }

    return result


# Update user performance record
def update_user_performance(db: Session, performance_id: int, performance: schemas.UserPerformanceCreate):
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
