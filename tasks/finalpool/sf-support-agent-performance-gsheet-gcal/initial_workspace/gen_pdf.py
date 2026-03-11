"""Generate Agent_Evaluation_Rubric.pdf."""
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
    "AGENT EVALUATION RUBRIC",
    "",
    "1. Purpose",
    "This rubric defines the criteria used to evaluate support agent performance",
    "on a monthly basis. Scorecards are reviewed by the support manager and",
    "discussed in the monthly Agent Performance Review meeting.",
    "",
    "2. Key Performance Indicators",
    "",
    "Ticket Volume",
    "  - Excellent: > 8000 tickets per month",
    "  - Good: 5000-8000 tickets per month",
    "  - Needs Improvement: < 5000 tickets per month",
    "",
    "Average Response Time",
    "  - Excellent: < 12 hours",
    "  - Good: 12-18 hours",
    "  - Needs Improvement: > 18 hours",
    "",
    "Customer Satisfaction (CSAT)",
    "  - Excellent: >= 4.0 (out of 5)",
    "  - Good: 3.0-3.9",
    "  - Needs Improvement: < 3.0",
    "",
    "SLA Compliance Rate",
    "  - Excellent: >= 30%",
    "  - Good: 20-30%",
    "  - Needs Improvement: < 20%",
    "",
    "SLA Thresholds by Priority:",
    "  - High: Response within 4 hours",
    "  - Medium: Response within 8 hours",
    "  - Low: Response within 24 hours",
    "",
    "3. Monthly Review Meeting",
    "The review meeting is scheduled 10 days after the monthly period launch.",
    "Attendees: support-manager@company.example.com",
    "Results distributed to: performance-review@company.example.com",
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Agent_Evaluation_Rubric.pdf")
make_pdf(out, "Agent Evaluation Rubric", lines)
print(f"Created: {out}")
