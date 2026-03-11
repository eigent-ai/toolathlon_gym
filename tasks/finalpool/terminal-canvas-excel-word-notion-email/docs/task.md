You are an academic advisor responsible for identifying students at risk of failing and coordinating early intervention efforts. Your goal is to perform a retention risk analysis across two specific courses, generate reports, build a tracking system, and notify the advising team.

Begin by reading the Retention_Policy.pdf in your workspace, which describes the intervention thresholds and escalation procedures your institution uses. Also review the scoring_model.json file, which contains the risk classification cutoffs and weighting parameters for the analysis.

Retrieve enrollment and grade data from the learning management system for two courses: course 16 (Foundations of Finance Fall 2013) and course 17 (Foundations of Finance Fall 2014). For each course, gather the course name, total enrollment count, and all student submission scores. Calculate the average score per student across all their graded submissions in each course.

Next, write a Python script called risk_scorer.py in your workspace and execute it using command-line tools. The script should classify each student based on their average score: students with an average below 60 are classified as High risk, students with an average between 60 and 74.99 are Medium risk, and students with an average of 75 or above are Low risk. The script should output the counts and percentages for each risk level per course and overall.

Create an Excel workbook called Student_Risk_Analysis.xlsx in your workspace with four sheets.

The first sheet should be named Course_Overview and contain columns for course_id, course_name, enrollment_count, avg_score, and pass_rate. Include one row for each of the two courses. The enrollment_count should reflect total enrolled students, avg_score should be the mean of all submission scores in the course, and pass_rate should be the percentage of students whose average score is 60 or above.

The second sheet should be named Risk_Distribution and contain columns for risk_level, student_count, and pct. Include one row for each risk level (High, Medium, Low) with the combined totals across both courses.

The third sheet should be named At_Risk_Students and contain columns for course_name, high_risk_count, medium_risk_count, and low_risk_count. Include one row for each course showing how many students fall into each risk category.

The fourth sheet should be named Intervention_Plan and contain columns for risk_level, action, timeline, and responsible. Include one row for each risk level describing the recommended intervention: High risk students should receive immediate one-on-one advising within one week by an academic advisor, Medium risk students should receive group tutoring sessions within two weeks by a course tutor, and Low risk students should receive a self-paced study resources email within one month by the student success office.

Create a Word document called Intervention_Plan.docx in your workspace. The document should contain a title "Student Retention Intervention Plan", a brief executive summary describing the analysis scope and key findings, a section on risk distribution summarizing the percentages across both courses, and a section detailing the recommended interventions for each risk level.

Set up a database in the team wiki system called "Student Risk Tracker" with properties for Student Course (title), Risk Level (select with options High, Medium, Low), Student Count (number), Average Score (number), and Pass Rate (number). Add one entry for each course with the aggregated data.

Finally, send an email to academic_advisors@university.edu with the subject "Student Retention Risk Analysis - Action Required" summarizing the key findings, including the total number of high-risk students across both courses and the recommended next steps.
