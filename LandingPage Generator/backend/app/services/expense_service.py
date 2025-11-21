from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..models.expense import Expense

class ExpenseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_expense(self, expense: Expense):
        expense_dict = expense.dict(by_alias=True)
        expense_dict["created_at"] = datetime.utcnow()
        expense_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.expenses.insert_one(expense_dict)
        expense_dict["_id"] = str(result.inserted_id)
        return expense_dict

    async def get_expense(self, expense_id: str):
        expense = await self.db.expenses.find_one({"_id": ObjectId(expense_id)})
        if expense:
            expense["_id"] = str(expense["_id"])
            return expense
        return None

    async def get_all_expenses(self, skip: int = 0, limit: int = 10):
        expenses = []
        cursor = self.db.expenses.find().skip(skip).limit(limit)
        async for expense in cursor:
            expense["_id"] = str(expense["_id"])
            expenses.append(expense)
        return expenses

    async def get_monthly_expenses(self, year: int, month: int):
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        expenses = []
        cursor = self.db.expenses.find({
            "date": {
                "$gte": start_date,
                "$lt": end_date
            }
        })
        async for expense in cursor:
            expense["_id"] = str(expense["_id"])
            expenses.append(expense)
        return expenses