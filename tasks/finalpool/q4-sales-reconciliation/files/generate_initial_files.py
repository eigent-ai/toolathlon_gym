"""
Generate the initial workspace PDF file: Q4_2025_Regional_Targets.pdf
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_targets_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Q4_2025_Regional_Targets.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=20, alignment=TA_CENTER, spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', parent=styles['Normal'],
        fontSize=12, alignment=TA_CENTER, spaceAfter=30, textColor=colors.grey
    )
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=9, alignment=TA_CENTER, textColor=colors.grey, spaceBefore=40
    )

    elements = []

    # Title
    elements.append(Paragraph("Q4 2025 Regional Revenue Targets", title_style))
    elements.append(Paragraph("Approved by Management - September 2025", subtitle_style))
    elements.append(Spacer(1, 20))

    # Table data
    data = [
        ["Region", "Revenue Target (USD)"],
        ["Asia Pacific", "$65,000.00"],
        ["Europe", "$60,000.00"],
        ["Latin America", "$55,000.00"],
        ["Middle East", "$50,000.00"],
        ["North America", "$55,000.00"],
        ["", ""],
        ["Total", "$285,000.00"],
    ]

    table = Table(data, colWidths=[3*inch, 2.5*inch])
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        # Total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        # Grid
        ('GRID', (0, 0), (-1, -3), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -3), [colors.white, colors.HexColor('#ECF0F1')]),
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))

    elements.append(table)

    # Footer note
    elements.append(Paragraph(
        "Targets are in USD. Performance measured by delivered orders only.",
        footer_style
    ))

    doc.build(elements)
    print(f"Created: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    create_targets_pdf()
