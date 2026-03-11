"""Generate groundtruth Excel for sf-hr-salary-benchmark-gform-excel-email."""
import os
import openpyxl

# Actual data from DB (sorted by Avg_Salary DESC)
DEPT_STATS = [
    # (Department, Headcount, Min_Salary, Max_Salary, Avg_Salary, Median_Salary)
    ("Engineering", 7096, 15360.00, 695267.00, 58991.61, 53603),
    ("HR",          7077, 18307.00, 692232.00, 58920.45, 53656),
    ("Sales",       7232, 15885.00, 652806.00, 58864.79, 53490),
    ("Support",     7244, 15916.00, 608157.00, 58400.48, 52944),
    ("R&D",         7083, 15128.00, 680490.00, 57905.93, 52404),
    ("Finance",     7148, 15760.00, 638897.00, 57878.19, 52987),
    ("Operations",  7120, 17168.00, 656505.00, 57808.74, 52293),
]

SUMMARY = [
    ("Total_Employees", 50000),
    ("Company_Avg_Salary", 58396.14),
    ("Highest_Paid_Dept", "Engineering"),
    ("Lowest_Paid_Dept", "Operations"),
]

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "groundtruth_workspace")
os.makedirs(out_dir, exist_ok=True)

wb = openpyxl.Workbook()

# Sheet 1: Department_Stats
ws_dept = wb.active
ws_dept.title = "Department_Stats"
ws_dept.append(["Department", "Headcount", "Min_Salary", "Max_Salary", "Avg_Salary", "Median_Salary"])
for row in DEPT_STATS:
    ws_dept.append(list(row))

# Sheet 2: Summary
ws_summary = wb.create_sheet("Summary")
ws_summary.append(["Metric", "Value"])
for row in SUMMARY:
    ws_summary.append(list(row))

wb.save(os.path.join(out_dir, "Salary_Analysis.xlsx"))
print("Groundtruth Excel created: Salary_Analysis.xlsx")
for row in SUMMARY:
    print(f"  {row[0]}: {row[1]}")
