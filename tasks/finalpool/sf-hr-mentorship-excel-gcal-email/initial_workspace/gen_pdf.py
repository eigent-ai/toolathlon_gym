"""Generate Mentorship_Guidelines.pdf."""
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
    "MENTORSHIP PROGRAM GUIDELINES",
    "",
    "Purpose",
    "The mentorship program pairs senior high-performers with junior employees to",
    "accelerate professional development and knowledge transfer.",
    "",
    "Mentor Criteria",
    "- Minimum 10 years of experience",
    "- Performance rating of 4 or above (on a 5-point scale)",
    "- Commitment to at least 2 hours per month for mentoring activities",
    "",
    "Mentee Criteria",
    "- 2 or fewer years of experience",
    "- Performance rating of 3 or above",
    "- Demonstrated motivation and eagerness to learn",
    "",
    "Pairing Process",
    "Pairs are matched sequentially by performance rank. Where possible, cross-department",
    "pairings are encouraged to broaden perspectives.",
    "",
    "Program Duration",
    "Each mentorship cycle runs for 6 months. Both parties commit to monthly check-ins",
    "and quarterly progress reviews.",
    "",
    "Kickoff Meeting",
    "All pairs attend a kickoff meeting 7 days after program launch to align on goals,",
    "discuss expectations, and set an initial meeting schedule.",
    "",
    "Communication",
    "All program updates are communicated via email to program@hr.example.com.",
    "Questions can be directed to hr@company.example.com.",
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Mentorship_Guidelines.pdf")
make_pdf(out, "Mentorship Program Guidelines", lines)
print(f"Created: {out}")
