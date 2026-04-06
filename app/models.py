from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class RoleEnum(str, enum.Enum):
    Admin = "Admin"
    Auditor = "Auditor"
    Viewer = "Viewer"
    Analyst = "Analyst"

class RecordTypeEnum(str, enum.Enum):
    Income = "Income"
    Expense = "Expense"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    is_active = Column(Integer, default=1)
    
    records = relationship("FinancialRecord", back_populates="user")

class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(RecordTypeEnum), nullable=False)
    category = Column(String(50), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="records")

class AuditorLog(Base):
    __tablename__ = "auditor_logs"

    id = Column(Integer, primary_key=True, index=True)
    auditor_id = Column(Integer, ForeignKey("users.id"))
    details = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
