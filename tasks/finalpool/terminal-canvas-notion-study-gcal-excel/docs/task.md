You are a university academic advisor helping students plan their study schedule for the upcoming semester. You need to analyze available course data, create a structured knowledge base, schedule study sessions, and produce a comprehensive study plan report.

Start by reading the Study_Planning_Guide.pdf in your workspace. It describes the methodology for allocating study time based on course complexity and assignment load.

Query the learning management system to retrieve information about the top five courses with the highest enrollment. For each course, get the course name, enrollment count, and the number of assignments and quizzes associated with it. The five courses you should focus on are the ones with IDs 7, 17, 4, 16, and 3 based on their high enrollment numbers.

For each of these five courses, also retrieve the list of assignments including their names and due dates. Get the quiz details as well, including quiz titles and point values.

Next, write and run a Python script called study_planner.py using command-line tools in your workspace. The script should take the course data you gathered and calculate a recommended weekly study hours value for each course. The formula is: base 3 hours per course, plus 0.5 hours for every assignment in the course, plus 1 hour for every quiz. The script should also assign a priority level to each course: High priority if weekly hours exceed 8, Medium if between 5 and 8, and Low if under 5.

Create a knowledge base by setting up a database in the team wiki called "Student Study Planner". The database should have properties for Course Name (title), Enrollment (number), Assignments (number), Quizzes (number), Weekly Hours (number), and Priority (select with options High, Medium, Low). Add one page entry for each of the five courses with the calculated values.

Schedule study sessions on the shared calendar for the week of March 9 to March 13, 2026. For each of the five courses, create one study session event. High priority courses get 2-hour sessions, Medium priority courses get 1.5-hour sessions, and Low priority courses get 1-hour sessions. Space them out across the week, starting at 9 AM on Monday and scheduling one per day. Each event summary should include the course name and "Study Session".

Create an Excel workbook called Study_Plan_Report.xlsx in your workspace with three sheets.

The first sheet should be named Course_Analysis and contain columns Course_Name, Enrollment, Assignments, Quizzes, Weekly_Hours, and Priority. Include one row for each of the five courses.

The second sheet should be named Weekly_Schedule and contain columns Day, Time, Course, Duration_Hours, and Session_Type. Include one row for each calendar event you created, showing Monday through Friday with the corresponding course study session details.

The third sheet should be named Priority_Matrix and contain columns Priority_Level, Course_Count, Total_Weekly_Hours, and Avg_Hours_Per_Course. Include one row each for High, Medium, and Low priority levels summarizing the courses in each category.
