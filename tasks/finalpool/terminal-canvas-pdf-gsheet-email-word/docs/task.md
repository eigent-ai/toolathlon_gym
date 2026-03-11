The academic affairs office needs a faculty workload analysis for the current term. There is a PDF document in the workspace called Course_Workload_Standards.pdf that contains institutional guidelines for maximum course assignments and acceptable workload ranges. Please read this PDF first to understand the standards.

Next, pull data from the learning management system. Get the list of all courses and for each course get the number of assignments, quizzes, and enrolled students. We need to understand which courses have the heaviest workload in terms of total items (assignments plus quizzes) and total student submissions.

Use command-line tools to create and run a Python script called workload_analyzer.py in the workspace. The script should read the course data from course_data.json (which you create from the LMS data) and the workload standards from standards.json (extracted from the PDF), compute workload metrics per course subject (group courses by subject name, removing the semester in parentheses), and output workload_analysis.json. Metrics to compute: average assignments per course, total students, and whether the workload exceeds standards.

Create a cloud spreadsheet called "Faculty_Workload_Tracker" with two sheets. The first sheet Course_Workload should have columns Course_Name, Subject, Semester, Assignment_Count, Quiz_Count, Total_Items, and Enrollment. Include all courses sorted alphabetically by Course_Name.

The second sheet Subject_Summary should have columns Subject, Num_Courses, Avg_Assignments, Total_Enrollment, Workload_Rating (set to "Heavy" if average assignments is 12 or more, "Moderate" if 8 to 11, "Light" if below 8). Sort alphabetically by Subject.

Create a Word document called Faculty_Workload_Report.docx with title "Faculty Workload Analysis Report" and sections for Overview (total courses, total assignments, total enrollments), Subject Analysis (discuss each subject's workload), High Workload Areas (identify subjects rated Heavy), and Recommendations (at least 3 actionable suggestions such as redistributing assignments or adding teaching assistants). Reference specific numbers from the analysis.

Send two emails. First, to department-chairs@university.edu with subject "Faculty Workload Analysis Complete" summarizing the total number of courses analyzed, subjects with Heavy workload, and top recommendation. Second, to academic-affairs@university.edu with subject "Workload Standards Compliance Report" noting which subjects comply with the standards and which exceed them.
