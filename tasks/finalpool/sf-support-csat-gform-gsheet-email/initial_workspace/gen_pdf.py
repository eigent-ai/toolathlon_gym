"""Generate SLA_Policy_Reference.pdf."""
import os
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4

def make_pdf(path, title, lines):
    c = rl_canvas.Canvas(path, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h - 50, title)
    c.setFont("Helvetica", 11)
    y = h - 80
    for line in lines:
        c.drawString(50, y, str(line))
        y -= 18
        if y < 80:
            c.showPage()
            y = h - 50
    c.save()

lines = [
    "SLA POLICY REFERENCE DOCUMENT",
    "",
    "1. Overview",
    "Service Level Agreements (SLAs) define the expected response and resolution",
    "times for support tickets based on their priority level.",
    "",
    "2. Priority Levels and SLA Thresholds",
    "",
    "HIGH PRIORITY",
    "  - Response Time SLA: 4 hours",
    "  - Resolution Time SLA: 24 hours",
    "  - Definition: Critical business impact, system outage, or data loss risk",
    "",
    "MEDIUM PRIORITY",
    "  - Response Time SLA: 8 hours",
    "  - Resolution Time SLA: 48 hours",
    "  - Definition: Significant impact on operations but workarounds available",
    "",
    "LOW PRIORITY",
    "  - Response Time SLA: 24 hours",
    "  - Resolution Time SLA: 72 hours",
    "  - Definition: Minor issues or feature requests with minimal business impact",
    "",
    "3. Compliance Measurement",
    "SLA compliance is measured as the percentage of tickets where the initial",
    "response was delivered within the specified SLA time window.",
    "",
    "4. Customer Satisfaction",
    "After ticket resolution, customers rate their experience on a 1-5 scale.",
    "Target average CSAT score: 4.0 or above.",
    "",
    "5. Reporting",
    "SLA compliance reports are sent to support-management@company.example.com.",
    "Analytics team contact: analytics@company.example.com.",
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SLA_Policy_Reference.pdf")
make_pdf(out, "SLA Policy Reference", lines)
print(f"Created: {out}")
