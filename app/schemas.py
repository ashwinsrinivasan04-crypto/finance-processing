from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from .models import RoleEnum, RecordTypeEnum

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    is_active: int

    class Config:
        from_attributes = True

class RecordCreate(BaseModel):
    amount: float
    type: RecordTypeEnum
    category: str
    date: Optional[datetime] = None
    notes: Optional[str] = None

class RecordResponse(BaseModel):
    id: int
    amount: float
    type: RecordTypeEnum
    category: str
    date: datetime
    notes: Optional[str]
    user_id: int

    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    category_wise_totals: dict

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AuditorLogCreate(BaseModel):
    details: str

class AuditorLogResponse(BaseModel):
    id: int
    auditor_id: int
    details: str
    timestamp: datetime

    class Config:
        from_attributes = True
