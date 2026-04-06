from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .. import models, schemas, auth, database

router = APIRouter(prefix="/records", tags=["Records"])

@router.post("/", response_model=schemas.RecordResponse)
def create_record(record: schemas.RecordCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.RoleChecker([models.RoleEnum.Admin]))):
    new_record = models.FinancialRecord(
        amount=record.amount,
        type=record.type,
        category=record.category,
        date=record.date or datetime.utcnow(),
        notes=record.notes,
        user_id=current_user.id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.get("/", response_model=List[schemas.RecordResponse])
def read_records(
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[models.RecordTypeEnum] = None,
    category: Optional[str] = None,
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.FinancialRecord)

    # Scoping logic
    if current_user.role == models.RoleEnum.Viewer:
        query = query.filter(models.FinancialRecord.user_id == current_user.id)
    # Admin, Auditor, Analyst see all records

    if type:
        query = query.filter(models.FinancialRecord.type == type)
    if category:
        query = query.filter(models.FinancialRecord.category.ilike(f"%{category}%"))

    records = query.offset(skip).limit(limit).all()

    if current_user.role == models.RoleEnum.Auditor:
        auth.log_auditor_action(db, current_user, "Auditor viewed the records list.")

    return records

@router.put("/{record_id}", response_model=schemas.RecordResponse)
def update_record(record_id: int, record_update: schemas.RecordCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.RoleChecker([models.RoleEnum.Admin]))):
    record = db.query(models.FinancialRecord).filter(models.FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record.amount = record_update.amount
    record.type = record_update.type
    record.category = record_update.category
    if record_update.date:
        record.date = record_update.date
    record.notes = record_update.notes

    db.commit()
    db.refresh(record)
    return record

@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.RoleChecker([models.RoleEnum.Admin]))):
    record = db.query(models.FinancialRecord).filter(models.FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully"}
