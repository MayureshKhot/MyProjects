from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.expense import Expense
from ..services.expense_service import ExpenseService
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..dependencies import get_database

router = APIRouter()

async def get_expense_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    return ExpenseService(db)

@router.post("/", response_model=Expense)
async def create_expense(
    expense: Expense,
    expense_service: ExpenseService = Depends(get_expense_service)
):
    return await expense_service.create_expense(expense)

@router.get("/{expense_id}", response_model=Expense)
async def get_expense(
    expense_id: str,
    expense_service: ExpenseService = Depends(get_expense_service)
):
    expense = await expense_service.get_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.get("/", response_model=List[Expense])
async def list_expenses(
    skip: int = 0,
    limit: int = 10,
    expense_service: ExpenseService = Depends(get_expense_service)
):
    return await expense_service.get_all_expenses(skip, limit)

@router.get("/monthly/{year}/{month}", response_model=List[Expense])
async def get_monthly_expenses(
    year: int,
    month: int,
    expense_service: ExpenseService = Depends(get_expense_service)
):
    return await expense_service.get_monthly_expenses(year, month)