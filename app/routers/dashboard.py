from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, auth, database

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    query = db.query(models.FinancialRecord)

    if current_user.role == models.RoleEnum.Viewer:
        query = query.filter(models.FinancialRecord.user_id == current_user.id)

    records = query.all()

    total_income = sum(r.amount for r in records if r.type == models.RecordTypeEnum.Income)
    total_expenses = sum(r.amount for r in records if r.type == models.RecordTypeEnum.Expense)
    net_balance = total_income - total_expenses

    # Category wise totals
    category_totals = {}
    for r in records:
        if r.category not in category_totals:
            category_totals[r.category] = 0
        if r.type == models.RecordTypeEnum.Income:
            category_totals[r.category] += r.amount
        else:
            category_totals[r.category] -= r.amount

    if current_user.role == models.RoleEnum.Auditor:
        auth.log_auditor_action(db, current_user, "Auditor viewed the dashboard summary.")

    return schemas.DashboardSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=net_balance,
        category_wise_totals=category_totals
    )
