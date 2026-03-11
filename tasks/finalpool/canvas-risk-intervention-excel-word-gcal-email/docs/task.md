I need to identify students at risk of academic failure and create an intervention plan. Pull student grade and submission data from the learning management system. Look at quiz scores, assignment completion rates, and overall grades across courses.

Use the terminal to create and run a Python script called risk_identifier.py in the workspace that reads student_performance.json (create it first), flags students with average scores below 50 as "Critical", between 50-65 as "At Risk", and above 65 as "On Track", calculates risk statistics per course, and outputs risk_assessment.json.

Create an Excel file called Student_Risk_Assessment.xlsx with four sheets. The first sheet Risk_Overview should have columns Course_Name, Total_Students, Critical_Count, At_Risk_Count, On_Track_Count, and Risk_Rate_Pct (round to 1 decimal, percentage of Critical + At Risk students), sorted by Risk_Rate_Pct descending. The second sheet Critical_Students should have columns Student_ID, Course_Name, Avg_Score (round to 1 decimal), Assignments_Submitted, and Late_Submissions for all Critical students. The third sheet Intervention_Plan should have Course_Name, Risk_Level, Recommended_Action, Responsible_Party, and Deadline columns. The fourth sheet Summary should have Metric and Value columns with Total_Students_Assessed, Critical_Students, At_Risk_Students, On_Track_Students, Overall_Risk_Rate_Pct (round to 1 decimal), and Highest_Risk_Course.

Create a Word document called Intervention_Report.docx with heading "Student Risk Intervention Report", sections for "Risk Assessment Methodology", "Course-Level Analysis", "Critical Cases", and "Recommended Interventions" with specific data.

Schedule a calendar event "Academic Intervention Planning Meeting" on March 13, 2026 from 3:00 PM to 4:30 PM UTC with description listing courses with highest risk rates.

Send an email to academic-affairs@university.edu with subject "Urgent: Student Risk Assessment Results" highlighting courses with risk rates above 40%.
