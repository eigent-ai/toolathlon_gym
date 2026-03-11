"""Generate Performance_Review_Criteria.pdf."""
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
    "PERFORMANCE REVIEW CRITERIA",
    "",
    "1. Rating Scale",
    "Employees are evaluated on a 5-point performance scale:",
    "  5 - Exceptional: Consistently exceeds expectations across all objectives",
    "  4 - Above Average: Frequently exceeds expectations",
    "  3 - Meets Expectations: Consistently delivers on objectives",
    "  2 - Below Expectations: Partially meets objectives; improvement needed",
    "  1 - Unsatisfactory: Fails to meet core objectives",
    "",
    "2. Classification for Board Review",
    "Top Performers: Rating of 5 (Exceptional)",
    "  - Eligible for merit increase and promotion consideration",
    "  - Recognized in department performance reports",
    "",
    "Underperformers: Rating of 1 or 2",
    "  - Subject to Performance Improvement Plan (PIP)",
    "  - Reviewed at Annual Performance Review Board Meeting",
    "",
    "3. Board Meeting Schedule",
    "The Annual Performance Review Board Meeting is held 21 days after the",
    "review cycle launch date. All department heads and HR executives attend.",
    "",
    "4. Data Requirements",
    "Reports must include per-department breakdowns of:",
    "  - Top performer count and average compensation",
    "  - Underperformer count and average compensation",
    "  - Overall department average performance rating",
    "",
    "5. Distribution",
    "Reports are submitted to executives@company.example.com",
    "from hr@company.example.com",
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Performance_Review_Criteria.pdf")
make_pdf(out, "Performance Review Criteria", lines)
print(f"Created: {out}")
