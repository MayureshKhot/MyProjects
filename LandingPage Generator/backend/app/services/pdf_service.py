from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from io import BytesIO
from ..models.invoice import Invoice

class PDFService:
    def _apply_template_style(self, template, elements, styles):
        style_dict = template["style"]
        primary_color = HexColor(style_dict["primary_color"])
        secondary_color = HexColor(style_dict["secondary_color"])
        font_family = style_dict["font_family"]
        
        # Create custom styles based on template
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_family,
            fontSize=24,
            textColor=primary_color,
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_family,
            fontSize=14,
            textColor=primary_color
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_family,
            fontSize=12
        )
        
        return title_style, heading_style, normal_style, primary_color, secondary_color

    def generate_invoice_pdf(self, invoice: Invoice, template: dict) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Apply template styles
        title_style, heading_style, normal_style, primary_color, secondary_color = \
            self._apply_template_style(template, elements, styles)

        # Header with template-specific styling
        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 20))

        # Company and Invoice Details
        elements.append(Paragraph("Invoice Details", heading_style))
        elements.append(Paragraph(f"Invoice Number: {invoice.invoice_number}", normal_style))
        elements.append(Paragraph(f"Date: {invoice.issue_date.strftime('%Y-%m-%d')}", normal_style))
        elements.append(Paragraph(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}", normal_style))
        elements.append(Spacer(1, 20))

        # Client Details with template styling
        elements.append(Paragraph("Bill To:", heading_style))
        elements.append(Paragraph(invoice.client_name, normal_style))
        elements.append(Paragraph(invoice.client_email, normal_style))
        elements.append(Paragraph(invoice.client_address, normal_style))
        elements.append(Spacer(1, 20))

        # Items Table with template colors
        table_data = [['Description', 'Quantity', 'Rate', 'Amount']]
        for item in invoice.items:
            table_data.append([
                item.description,
                str(item.quantity),
                f"₹{item.rate:,.2f}",
                f"₹{item.amount:,.2f}"
            ])

        table = Table(table_data, colWidths=[250, 70, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), template["style"]["font_family"]),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), secondary_color),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), template["style"]["font_family"]),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, primary_color)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Totals with template styling
        elements.append(Paragraph(f"Subtotal: ₹{invoice.subtotal:,.2f}", normal_style))
        elements.append(Paragraph(f"Tax Rate: {invoice.tax_rate}%", normal_style))
        elements.append(Paragraph(f"Tax Amount: ₹{invoice.tax_amount:,.2f}", normal_style))
        elements.append(Paragraph(f"Total Amount: ₹{invoice.total_amount:,.2f}", heading_style))

        if invoice.notes:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Notes:", heading_style))
            elements.append(Paragraph(invoice.notes, normal_style))

        if template["style"]["layout"] == "modern":
            elements.append(Spacer(1, 40))
            elements.append(Paragraph("Thank you for your business!", heading_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer