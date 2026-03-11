I need to create a comprehensive grade report for our department heads. Pull grade and enrollment data from the learning management system for all courses. Get assignment scores, quiz results, and overall grades.

Use the terminal to create and run a Python script called grade_reporter.py in the workspace that reads grade_data.json (create it first), calculates grade distributions (A: 90+, B: 80-89, C: 70-79, D: 60-69, F: below 60), pass rates, and course averages, and outputs grade_report.json.

Create a Google Sheet titled "Department Grade Dashboard" with two sheets. The first sheet Grade_Distribution should have columns Course_Name, A_Count, B_Count, C_Count, D_Count, F_Count, Total_Students, Pass_Rate_Pct (round to 1 decimal, pass means C or above), and Course_Avg (round to 1 decimal), sorted by Course_Name. The second sheet Department_Summary should have Metric and Value columns with Total_Courses, Total_Students, Overall_Pass_Rate (round to 1 decimal), Overall_Avg_Grade (round to 1 decimal), Highest_Avg_Course, and Lowest_Avg_Course.

Also read the Course_Policies.pdf in the workspace which has the grade scale and academic policies, and make sure the grade thresholds you use match those defined in the policy document.

Send an email to dept-heads@university.edu with subject "Q1 2026 Grade Distribution Report" including a summary of the overall pass rate, highest and lowest performing courses, and a note about courses with pass rates below 70% requiring review.
