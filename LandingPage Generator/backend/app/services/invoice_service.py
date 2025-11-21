from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..models.invoice import Invoice

class InvoiceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_invoice(self, invoice: Invoice):
        invoice_dict = invoice.dict(by_alias=True)
        invoice_dict["created_at"] = datetime.utcnow()
        invoice_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.invoices.insert_one(invoice_dict)
        invoice_dict["_id"] = str(result.inserted_id)
        return invoice_dict

    async def get_invoice(self, invoice_id: str):
        invoice = await self.db.invoices.find_one({"_id": ObjectId(invoice_id)})
        if invoice:
            invoice["_id"] = str(invoice["_id"])
            return invoice
        return None

    async def get_all_invoices(self, skip: int = 0, limit: int = 10):
        invoices = []
        cursor = self.db.invoices.find().skip(skip).limit(limit)
        async for invoice in cursor:
            invoice["_id"] = str(invoice["_id"])
            invoices.append(invoice)
        return invoices

    async def update_invoice_status(self, invoice_id: str, status: str):
        result = await self.db.invoices.update_one(
            {"_id": ObjectId(invoice_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return True