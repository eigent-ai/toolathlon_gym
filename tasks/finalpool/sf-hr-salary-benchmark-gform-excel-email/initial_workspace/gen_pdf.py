"""Generate Compensation_Policy.pdf."""
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
    "COMPENSATION POLICY",
    "",
    "1. Philosophy",
    "Our compensation philosophy aims to attract, retain, and motivate top talent",
    "by offering competitive and equitable pay aligned with market benchmarks.",
    "",
    "2. Salary Bands",
    "Salaries are set based on role, department, experience level, and performance.",
    "Annual reviews ensure salaries remain competitive within the industry.",
    "",
    "3. Department Benchmarks",
    "Each department is benchmarked against industry data annually. Departments",
    "showing significant deviation from market rates are prioritized for adjustment.",
    "",
    "4. Performance-Linked Pay",
    "High performers (rating 4-5) are eligible for merit increases of up to 10%.",
    "Underperformers may have their compensation reviewed after a performance",
    "improvement plan is completed.",
    "",
    "5. Transparency",
    "Employees are encouraged to discuss compensation concerns with their managers.",
    "HR conducts an annual compensation satisfaction survey to gather feedback.",
    "",
    "6. Equity Review",
    "HR performs annual pay equity analyses across departments, roles, and demographics",
    "to identify and address any unjustified pay gaps.",
    "",
    "Contact: compensation@hr.example.com",
    "Leadership distribution: hr-leadership@company.example.com",
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Compensation_Policy.pdf")
make_pdf(out, "Compensation Policy", lines)
print(f"Created: {out}")
