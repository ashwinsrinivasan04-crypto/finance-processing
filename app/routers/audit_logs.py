from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth, database

router = APIRouter(prefix="/audit-logs", tags=["Auditor Logs"])

@router.post("/", response_model=schemas.AuditorLogResponse)
def create_audit_log(log: schemas.AuditorLogCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.RoleChecker([models.RoleEnum.Auditor]))):
    new_log = models.AuditorLog(
        auditor_id=current_user.id,
        details=log.details
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.get("/", response_model=List[schemas.AuditorLogResponse])
def read_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.RoleChecker([models.RoleEnum.Admin, models.RoleEnum.Auditor]))):
    logs = db.query(models.AuditorLog).offset(skip).limit(limit).all()
    if current_user.role == models.RoleEnum.Auditor:
        auth.log_auditor_action(db, current_user, "Auditor viewed the auditor logs.")
    return logs
