You are the Learning and Development Director for a large organization. Your goal is to identify skills gaps across departments by cross-referencing employee performance data with available training courses, then communicate targeted recommendations to department heads.

Begin by visiting the company's internal skills framework portal at http://localhost:30237 to review the required skills for each department along with the expected proficiency levels. The portal has two pages: the main page showing required skills by department, and a training page at http://localhost:30237/training.html that maps specific training courses to each skill area.

Next, query the employee data warehouse to get a comprehensive picture of each department's workforce. You need the department names, employee counts, average performance ratings, and the distribution of education levels (how many employees hold each education level such as High School, Diploma, Bachelor's, Master's, or PhD). Focus on all seven departments in the system.

Then check the learning management system to see what courses are currently available. For each course, note the enrollment count (total students), the number of assignments, and whether the course has quizzes available. This helps determine how robust the training offerings are.

Using the skills assessment methodology described in the notes file in your workspace, calculate a gap score for each department based on the threshold and formula specified there. The gap score is calculated by subtracting the department average performance rating from the threshold, with a minimum of 0. Higher gap scores indicate more urgent training needs.

Create an Excel file called Skills_Gap.xlsx in your workspace with three sheets. The first sheet should be called "Department Skills" with columns for Department, Required_Skills (a comma-separated list from the portal), Employee_Count, Avg_Performance, Education_Distribution (a text summary), and Gap_Score. Include all seven departments.

The second sheet should be called "Training Mapping" with columns for Skill_Area, Mapped_Course (from the training portal), Total_Students, Assignment_Count, and Has_Quizzes. This maps each required skill to the closest matching course in the learning system.

The third sheet should be called "Priority Actions" with columns for Department, Gap_Score, Priority (High if gap score is above 0 even slightly, Low if gap score is 0), Recommended_Training, and Contact_Email (from the department heads file).

Finally, send an email to each department head whose department has a non-zero gap score. Each email should have a subject line that includes the department name and the phrase "Training Recommendations", and the body should summarize the skills gap findings and suggest relevant courses. Use the email addresses from the department heads file in your workspace.

When you have completed all tasks, call claim_done.
