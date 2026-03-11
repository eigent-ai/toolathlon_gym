The Office of Academic Affairs is conducting its annual review of course offerings and wants to compare our university's course metrics against national benchmarks. A benchmarking service provides national averages through a REST API endpoint at http://localhost:30203/api/benchmarks.json, which returns data including national average enrollment, assignment counts, and quiz counts for seven course discipline areas.

Our university offers 22 courses through our learning management system across seven distinct course types. We need to understand how our courses compare to national standards in terms of enrollment numbers, number of assignments, and number of quizzes.

Start by fetching the national benchmark data from the API endpoint. Then retrieve the full list of courses from the university learning management system. For each course, note the course name, total student enrollment, and count the number of assignments and quizzes associated with it. Group the courses by their course type (the part of the course name before the semester and year in parentheses, for example "Foundations of Finance" from "Foundations of Finance (Fall 2013)") and compute the average enrollment, average assignment count, and average quiz count per course type.

Create an Excel file called "Course_Benchmark_Analysis.xlsx" in the workspace with three sheets.

The first sheet called "National Benchmarks" should have columns Course_Type, Discipline, National_Avg_Enrollment, National_Avg_Assignments, and National_Avg_Quizzes, populated with the benchmark API data for all seven course types.

The second sheet called "Our Courses" should list all 22 individual courses with columns Course_Name, Course_Type, Enrollment, Assignment_Count, and Quiz_Count.

The third sheet called "Comparison" should have columns Course_Type, Our_Avg_Enrollment, National_Avg_Enrollment, Enrollment_Diff, Our_Avg_Assignments, National_Avg_Assignments, Assignment_Diff, Our_Avg_Quizzes, National_Avg_Quizzes, and Quiz_Diff. The difference columns should be calculated as our average minus the national average. There should be 7 rows, one for each course type.

Next, create a PowerPoint presentation called "Academic_Benchmark_Presentation.pptx" in the workspace. The presentation should have a title slide with the title "Course Benchmark Analysis" and a subtitle referencing the academic year. Include one slide per course type (7 slides) showing the course type name as the title and a brief comparison of enrollment and assignment metrics versus national benchmarks. Add a final summary slide identifying which course types exceed national benchmarks in enrollment and which fall below.

Finally, send an email from academic-affairs@university.edu to dean@university.edu with the subject "Annual Course Benchmark Report". The body should summarize which course types are above and below national enrollment benchmarks.

Save all output files to the workspace directory.
