from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class InvoiceStatus(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    OVERDUE = "overdue"

class InvoiceItem(BaseModel):
    description: str
    quantity: float
    rate: float
    amount: float

class Invoice(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    invoice_number: str
    client_name: str
    client_email: str
    client_address: str
    issue_date: datetime
    due_date: datetime
    items: List[InvoiceItem]
    subtotal: float
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    total_amount: float
    notes: Optional[str] = None
    terms: Optional[str] = None
    status: InvoiceStatus = InvoiceStatus.UNPAID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True  # Updated from allow_population_by_field_name