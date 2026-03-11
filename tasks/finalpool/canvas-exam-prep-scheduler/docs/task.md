The academic coordinator needs to organize exam review sessions for courses where students are struggling on quizzes. Start by fetching the preparation guidelines from http://localhost:30218/api/prep_guidelines.json which specify the focus threshold, session duration, and scheduling parameters.

Next, analyze quiz performance data from the learning management system. Focus only on quizzes that use a 100-point scale for consistent comparison. Calculate the average score for each quiz and identify which quizzes fall below the focus threshold specified in the guidelines. Determine which courses have at least one quiz below the threshold and therefore need review sessions.

Review the scheduling rules document and room information file in the workspace to understand the available time slots and room capacities.

Create an Excel file called Exam_Prep.xlsx with three sheets. The first sheet named "Quiz Performance" should contain columns for Course, Quiz, Avg_Score, and Below_Threshold (Yes or No based on the focus threshold from the guidelines). Include only quizzes scored on the 100-point scale, sorted by course name then quiz name. The second sheet named "Review Schedule" should list one review session per course that needs review, with columns for Course, Topic (formatted as "Quiz Review" followed by the course subject), Date (starting from 2026-03-16, weekdays only), Time (using the preferred afternoon slot from the guidelines), and Room (cycling through available rooms). The third sheet named "Summary" should have rows for Total_Quizzes_Analyzed, Below_Threshold_Quizzes, Courses_Needing_Review, and Review_Sessions_Scheduled.

For each course that needs a review session, create a calendar event with the course name and "Quiz Review Session" in the title, set to the date and time listed in the Review Schedule sheet. The event description should mention the average quiz score that triggered the review.

Finally, send an email to academic-coordinator@university.edu with subject "Exam Review Sessions Scheduled" summarizing the number of review sessions planned and which courses they cover.
