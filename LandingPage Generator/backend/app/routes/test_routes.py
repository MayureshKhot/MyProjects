from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from ..models.invoice import Invoice, InvoiceItem
from ..services.invoice_service import InvoiceService
from ..services.template_service import TemplateService
from ..services.pdf_service import PDFService
from fastapi.responses import StreamingResponse
from ..dependencies import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

async def get_invoice_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    return InvoiceService(db)

async def get_template_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    return TemplateService(db)

@router.get("/generate-sample-invoice")
async def generate_sample_invoice(
    invoice_service: InvoiceService = Depends(get_invoice_service),
    template_service: TemplateService = Depends(get_template_service)
):
    # Initialize template service
    await template_service.initialize()
    
    # Create sample invoice data
    sample_invoice = Invoice(
        invoice_number="INV-2024-001",
        client_name="John Doe",
        client_email="john@example.com",
        client_address="123 Main St, City, Country",
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        items=[
            InvoiceItem(
                description="Web Development",
                quantity=1,
                rate=5000.00,
                amount=5000.00
            ),
            InvoiceItem(
                description="UI/UX Design",
                quantity=2,
                rate=2500.00,
                amount=5000.00
            )
        ],
        subtotal=10000.00,
        tax_rate=18.0,
        tax_amount=1800.00,
        total_amount=11800.00,
        notes="Thank you for your business!"
    )

    # Save invoice
    created_invoice = await invoice_service.create_invoice(sample_invoice)

    # Get default template
    templates = await template_service.get_all_templates()
    template = templates[0] if templates else None

    if not template:
        raise HTTPException(status_code=404, detail="No template found")

    # Generate PDF
    pdf_service = PDFService()
    pdf_buffer = pdf_service.generate_invoice_pdf(Invoice(**created_invoice), template)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=sample_invoice.pdf"
        }
    )