"""Generate Performance_Criteria.pdf for sf-support-agent-review task."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

TASK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(TASK_ROOT, "initial_workspace")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_path = os.path.join(OUTPUT_DIR, "Performance_Criteria.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=18,
                                  spaceAfter=20)
    heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading2"],
                                    fontSize=14, spaceAfter=10, spaceBefore=15)
    body_style = styles["BodyText"]

    elements = []

    elements.append(Paragraph("Support Team Performance Evaluation Criteria", title_style))
    elements.append(Paragraph("Q1 2026 Quarterly Review Framework", styles["Heading3"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("1. Overview", heading_style))
    elements.append(Paragraph(
        "This document defines the evaluation framework used to assess support team performance "
        "during the quarterly review cycle. Each metric is measured at the priority level to ensure "
        "that high-priority incidents receive appropriate attention and that service level agreements "
        "are being met across all severity tiers.", body_style))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("2. Key Performance Metrics", heading_style))
    elements.append(Paragraph(
        "The following metrics are tracked for each priority level (High, Medium, Low):", body_style))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("<b>Ticket Volume:</b> The total number of tickets received at each "
                              "priority level during the review period. This metric helps identify "
                              "workload distribution and staffing needs.", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>Average Response Time (Hours):</b> The mean time between ticket "
                              "creation and first response, measured in hours and rounded to two "
                              "decimal places. Target response times vary by priority.", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>Customer Satisfaction Score:</b> The average satisfaction rating "
                              "provided by customers after ticket resolution, on a scale of 1 to 5, "
                              "rounded to two decimal places.", body_style))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("3. SLA Response Targets", heading_style))
    sla_data = [
        ["Priority", "Target Response (Hours)", "Target Resolution (Hours)"],
        ["Critical", "1", "4"],
        ["High", "4", "24"],
        ["Medium", "8", "48"],
        ["Low", "24", "72"],
    ]
    sla_table = Table(sla_data, colWidths=[1.5*inch, 2*inch, 2*inch])
    sla_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ecf0f1")]),
    ]))
    elements.append(sla_table)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("4. Agent Roster Expectations", heading_style))
    elements.append(Paragraph(
        "All active support agents should be included in the review. The agent roster includes "
        "their name, team assignment (Specialist, Tier 2, or Tier 3), and skill level (junior, "
        "mid, or senior). Agents are expected to be aware of the overall team performance across "
        "all priority levels.", body_style))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("5. Reporting Requirements", heading_style))
    elements.append(Paragraph(
        "The quarterly review report should be compiled into an Excel spreadsheet with separate "
        "sheets for ticket summary statistics and the agent roster. Individual notification emails "
        "should be sent to each agent with the team-wide performance data.", body_style))

    doc.build(elements)
    print(f"Generated: {pdf_path}")


if __name__ == "__main__":
    main()
