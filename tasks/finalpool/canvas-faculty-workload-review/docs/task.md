The provost wants to review faculty workload balance across all departments. Start by fetching the faculty workload standards from http://localhost:30220/api/workload_standards.json which defines the maximum course load, student thresholds, grading time estimates, and overload criteria.

Then query the learning management system to determine each instructor's teaching load. For each instructor with a teaching role, count the number of distinct courses they teach, the total number of students across those courses, and the total number of assignments they are responsible for. Calculate the estimated total semester grading hours as total students multiplied by the grading hours per student from the standards. Then calculate the weekly grading hours by dividing the semester total by the number of semester weeks from the standards. An instructor is overloaded if they teach more than the maximum courses allowed OR if their weekly grading hours exceed the maximum weekly hours from the standards.

Review the workload policy document and faculty directory file in the workspace for context on department assignments and institutional policy.

Create an Excel file called Faculty_Workload.xlsx with two sheets. The first sheet named "Instructor Load" should contain columns for Instructor, Courses_Count, Total_Students, Total_Assignments, Est_Grading_Hours (total semester hours), Weekly_Grading_Hours, and Overloaded_YN. Sort alphabetically by instructor name. The second sheet named "Department Summary" should aggregate by department (based on the course subject area) with columns for Department, Instructor_Count, Course_Count, and Total_Students.

Write the workload data to a shared spreadsheet titled "Faculty Workload Analysis" with a sheet called "Instructor Load" containing the same instructor-level data.

Also create a presentation called Workload_Review.pptx summarizing the key findings. Include a title slide, a slide showing the total number of instructors and how many are overloaded, a slide with the department-level breakdown, and a recommendations slide suggesting rebalancing strategies for departments with overloaded faculty.
