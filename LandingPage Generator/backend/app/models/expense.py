from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ExpenseCategory(str, Enum):
    OFFICE_SUPPLIES = "office_supplies"
    MARKETING = "marketing"
    TRAVEL = "travel"
    UTILITIES = "utilities"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    OTHERS = "others"

class TaxCategory(str, Enum):
    DEDUCTIBLE = "deductible"
    NON_DEDUCTIBLE = "non_deductible"
    CAPITAL_EXPENSE = "capital_expense"

class Expense(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    amount: float
    description: str
    category: ExpenseCategory
    tax_category: TaxCategory
    date: datetime
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True