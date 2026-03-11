The curriculum review committee has asked me to assess whether our university courses meet the accreditation standards published by the academic board. The accreditation requirements are posted on a standards page at http://localhost:30210/standards.html which lists the minimum number of assignments and quizzes required per course, along with other quality metrics.

Please start by visiting that accreditation standards page and extracting all the compliance criteria listed there. The page specifies minimum assignment counts, minimum quiz counts, and other requirements that each course must meet to be considered compliant.

Next, query the learning management system to get information about all courses currently in the system. For each course, I need the course name, the number of assignments, and the number of quizzes. There are 22 courses total across several departments and semesters.

Using the standards from the website, evaluate each course against the accreditation criteria. A course passes if it meets all the minimum requirements, and fails if it does not meet at least one requirement.

Create a Word document called Accreditation_Compliance_Report.docx in the workspace. The document should have a title "University Course Accreditation Compliance Report", an introduction explaining the purpose of the review and the source of the standards, and then a section for each course showing the course name, assignment count, quiz count, and whether it passes or fails each criterion. Include a summary at the end with the total number of compliant courses, non-compliant courses, and the overall compliance rate as a percentage.

Then create a database in the knowledge base called "Course Compliance Tracker" with the following properties: Course_Name (title), Department (rich_text), Assignment_Count (number), Quiz_Count (number), Assignments_Compliant (checkbox), Quizzes_Compliant (checkbox), Overall_Status (select with options "Compliant" or "Non-Compliant"), and Follow_Up_Date (date). Add an entry for each of the 22 courses. Set Follow_Up_Date to April 15, 2026 for non-compliant courses and leave it empty for compliant ones.

Finally, for each unique department that has at least one non-compliant course, send an email from accreditation@university.edu to department-review@university.edu with the subject "Accreditation Review: [Department Name] Courses" listing the non-compliant courses in that department and what standards they failed to meet.
