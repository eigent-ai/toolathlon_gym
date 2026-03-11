"""
Generate groundtruth Excel file for the canvas-course-feedback task.
"""

import openpyxl
import os

COURSES = [
    ("AAA-2014J", "Applied Analytics & Algorithms", 365, 67.85, 6, 0),
    ("BBB-2014J", "Biochemistry & Bioinformatics", 2292, 64.31, 6, 0),
    ("CCC-2014J", "Creative Computing & Culture", 2498, 70.22, 10, 4),
    ("DDD-2014J", "Data-Driven Design", 1803, 69.99, 7, 0),
    ("EEE-2014J", "Environmental Economics & Ethics", 1188, 81.27, 5, 0),
    ("FFF-2014J", "Foundations of Finance", 2365, 76.51, 13, 7),
    ("GGG-2014J", "Global Governance & Geopolitics", 749, 76.60, 10, 6),
]

def main():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Course Statistics"

    headers = [
        "Course_Code",
        "Course_Name",
        "Enrollment",
        "Avg_Score",
        "Assignment_Count",
        "Quiz_Count",
        "Total_Assessments",
    ]
    ws.append(headers)

    for code, name, enrollment, avg_score, assign_count, quiz_count in COURSES:
        total = assign_count + quiz_count
        ws.append([code, name, enrollment, avg_score, assign_count, quiz_count, total])

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "Fall_2014_Course_Report.xlsx")
    wb.save(output_path)
    print(f"Groundtruth Excel saved to: {output_path}")


if __name__ == "__main__":
    main()
