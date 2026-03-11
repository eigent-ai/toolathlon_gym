A culinary arts program coordinator needs to prepare a comprehensive course review that combines student assignment data with recipe database analysis. The review covers two biochemistry and bioinformatics courses from the learning management system (course IDs 3 and 4) and recipe information from the cooking database.

Start by reviewing the assessment rubric and course configuration file in the workspace.

For the course data, pull all assignments from both courses including the assignment name, point value, and number of student submissions. For the recipe data, retrieve a summary of all recipe categories showing the number of recipes and average difficulty level per category.

Run analysis scripts that compute summary statistics: total assignments per course, average points per assignment, total submissions, and a breakdown of recipe categories by count and difficulty.

Create an Excel file called Nutrition_Course_Assessment.xlsx with four sheets. The first sheet "Student_Assignments" should have columns Course_Name, Assignment_Name, Points_Possible, and Submission_Count, listing all assignments from both courses sorted by Course_Name then Assignment_Name. The second sheet "Recipe_Analysis" should have columns Category, Recipe_Count, and Avg_Difficulty (rounded to 1 decimal), listing all recipe categories sorted by Category. The third sheet "Course_Summary" should have columns Metric and Value with the following rows: Total_Courses (value 2), Course_3_Assignments (number of assignments in course 3), Course_4_Assignments (number of assignments in course 4), Course_3_Total_Submissions (total submissions across all course 3 assignments), Course_4_Total_Submissions (total submissions across all course 4 assignments), Total_Recipe_Categories (number of categories), Total_Recipes (total recipe count). The fourth sheet "Grading_Schedule" should have columns Date, Time, Course_Name, Assignment_Name, and Duration_Minutes, scheduling grading sessions for each assignment of course 3 starting from March 10 2026 at 09:00, with one assignment per session lasting 60 minutes, one session per day on weekdays only, sorted by date.

Also write a Word document called Assessment_Feedback.docx that summarizes the course assignment structure, discusses the distribution of recipe categories and difficulty levels, and provides recommendations for how the recipe database could complement the course curriculum.

Finally, create calendar events for each grading session listed in the Grading_Schedule sheet so the coordinator can track them.
