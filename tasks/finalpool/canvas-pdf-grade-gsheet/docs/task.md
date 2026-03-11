I am a course administrator at Open University and I need to generate end-of-semester grade reports for all Spring 2014 courses. The Spring 2014 courses are identified by course codes containing "2014B".

There is a grading_policy.pdf file in the workspace that contains our official grading scale and special designation criteria. Please read it first to understand the grade boundaries and honors and probation rules.

For each Spring 2014 course, look up the course in our learning management system and find the lead instructor. The lead instructor is the teacher enrolled in the course who comes first alphabetically by name. If a course has no teacher enrolled, use "N/A" for the instructor name and email, and skip sending an email for that course. Also find the number of students who have recorded scores (a non-null current_score in their enrollment grades) and calculate the class average score from those student scores.

Assign each course a letter grade based on its class average using the scale in the PDF. Also determine if the course qualifies for "With Distinction" honors or triggers an "Academic Probation" flag per the PDF criteria.

Create a file called semester_grade_report.xlsx in the workspace with three sheets.

The first sheet should be named "Course Grades" with the following columns: Course_Code, Course_Name, Lead_Instructor, Instructor_Email, Students_Scored, Class_Average (rounded to 2 decimal places), Letter_Grade, Distinction (write "Yes" or "No"), Probation (write "Yes" or "No"). Sort rows by Course_Code alphabetically.

The second sheet should be named "Grade Distribution" with columns: Letter_Grade (list A, B, C, D, F in that order), Course_Count (how many courses received that letter grade), Courses (comma-separated course codes that received that grade, sorted alphabetically within each grade; leave empty string if no courses got that grade).

The third sheet should be named "Summary" with two columns (Metric, Value) containing the following rows: Total_Courses (the number of Spring 2014 courses), Avg_Class_Average (the average of all class averages rounded to 2 decimal places), Highest_Average_Course (the course code with the highest class average), Lowest_Average_Course (the course code with the lowest class average), Distinction_Count (how many courses earned the With Distinction designation), Probation_Count (how many courses are flagged for Academic Probation).

Also create a Google Sheet titled "Spring 2014 Grade Summary" with one sheet named "Grades" containing columns: Course_Code, Class_Average, Letter_Grade, Distinction, Probation for all six courses sorted by Course_Code.

Finally, send an email from registrar@openuniversity.ac.uk to each course's lead instructor (for courses that have a teacher) with the subject "End-of-Semester Grade Report: [Course Code]" where [Course Code] is replaced with the actual course code. The body should state the course name, the class average, the letter grade, and whether the course earned distinction or is on academic probation.
