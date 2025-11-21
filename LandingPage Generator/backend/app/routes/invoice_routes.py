from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from ..models.invoice import Invoice
from ..models.template import InvoiceTemplate
from ..services.invoice_service import InvoiceService
from ..services.template_service import TemplateService
from ..services.pdf_service import PDFService
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..dependencies import get_database

router = APIRouter()

async def get_invoice_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    return InvoiceService(db)

@router.post("/", response_model=Invoice)
async def create_invoice(
    invoice: Invoice,
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    return await invoice_service.create_invoice(invoice)

@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(
    invoice_id: str,
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    invoice = await invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.get("/", response_model=List[Invoice])
async def list_invoices(
    skip: int = 0,
    limit: int = 10,
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    return await invoice_service.get_all_invoices(skip, limit)

@router.patch("/{invoice_id}/status")
async def update_invoice_status(
    invoice_id: str,
    status: str,
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    return await invoice_service.update_invoice_status(invoice_id, status)

@router.get("/templates", response_model=List[InvoiceTemplate])
async def get_template_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    return TemplateService(db)

@router.get("/templates", response_model=List[InvoiceTemplate])
async def get_invoice_templates(
    template_service: TemplateService = Depends(get_template_service)
):
    return await template_service.get_all_templates()

@router.get("/{invoice_id}/pdf/{template_id}")
async def generate_invoice_pdf_with_template(
    invoice_id: str,
    template_id: str,
    invoice_service: InvoiceService = Depends(get_invoice_service),
    template_service: TemplateService = Depends(get_template_service)
):
    invoice = await invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    template = await template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_invoice_pdf(Invoice(**invoice), template)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice['invoice_number']}.pdf"
        }
    )