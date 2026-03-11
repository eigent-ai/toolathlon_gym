"""Generate groundtruth Excel for sf-hr-mentorship-excel-gcal-email."""
import os
import openpyxl

# Actual data from DB queries
MENTORS = [
    ("Olivia Walker", "R&D", 5, 54),
    ("David Thompson", "Support", 5, 45),
    ("Ananya Taylor", "HR", 5, 44),
    ("Sarah Smith", "Engineering", 5, 43),
    ("Rohit Sharma", "Engineering", 5, 42),
    ("Vikram Singh", "HR", 5, 41),
    ("Kiran Thompson", "Sales", 5, 39),
    ("David Williams", "Support", 5, 39),
    ("Ananya Singh", "Operations", 5, 38),
    ("Kiran Walker", "Sales", 5, 38),
]

MENTEES = [
    ("Luke Iyer", "R&D", 5, 1),
    ("David Sharma", "R&D", 5, 0),
    ("Sarah Thomas", "R&D", 5, 0),
    ("Linda Smith", "R&D", 5, 0),
    ("John Brown", "R&D", 5, 0),
    ("John Taylor", "R&D", 5, 0),
    ("Nina Smith", "R&D", 5, 0),
    ("Leo Taylor", "R&D", 5, 0),
    ("Sarah Williams", "R&D", 5, 0),
    ("Olivia Miller", "R&D", 5, 0),
]

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "groundtruth_workspace")
os.makedirs(out_dir, exist_ok=True)

wb = openpyxl.Workbook()

# Sheet 1: Pairs
ws_pairs = wb.active
ws_pairs.title = "Pairs"
ws_pairs.append(["Mentor_Name", "Mentor_Department", "Mentor_Rating", "Mentee_Name", "Mentee_Department", "Mentee_Experience"])
for i in range(10):
    mentor = MENTORS[i]
    mentee = MENTEES[i]
    ws_pairs.append([mentor[0], mentor[1], mentor[2], mentee[0], mentee[1], mentee[3]])

# Sheet 2: Program_Summary
ws_summary = wb.create_sheet("Program_Summary")
ws_summary.append(["Metric", "Value"])
total_pairs = 10
avg_mentor_rating = round(sum(m[2] for m in MENTORS) / len(MENTORS), 2)
avg_mentee_exp = round(sum(m[3] for m in MENTEES) / len(MENTEES), 2)
ws_summary.append(["Total_Pairs", total_pairs])
ws_summary.append(["Avg_Mentor_Rating", avg_mentor_rating])
ws_summary.append(["Avg_Mentee_Experience", avg_mentee_exp])

wb.save(os.path.join(out_dir, "Mentorship_Pairs.xlsx"))
print("Groundtruth Excel created.")
print(f"  Total_Pairs: {total_pairs}")
print(f"  Avg_Mentor_Rating: {avg_mentor_rating}")
print(f"  Avg_Mentee_Experience: {avg_mentee_exp}")
