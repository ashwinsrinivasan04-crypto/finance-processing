from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth, database

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.RoleChecker([models.RoleEnum.Admin]))):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password, 
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.RoleChecker([models.RoleEnum.Admin, models.RoleEnum.Auditor]))):
    users = db.query(models.User).offset(skip).limit(limit).all()
    if current_user.role == models.RoleEnum.Auditor:
        auth.log_auditor_action(db, current_user, "Auditor viewed the user list.")
    return users

@router.put("/{user_id}/status", response_model=schemas.UserResponse)
def change_user_status(user_id: int, is_active: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.RoleChecker([models.RoleEnum.Admin]))):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
