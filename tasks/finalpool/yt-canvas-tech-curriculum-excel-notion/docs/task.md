Our university wants to enhance programming and computing courses with curated supplemental video resources from a tech education YouTube channel.

From the learning management system, retrieve all active courses whose names contain any of these keywords: Analytics, Algorithms, Computing, Data, or Software. Then retrieve all available Fireship videos from the video database.

For each course found, identify the two or three most relevant Fireship videos by matching course name keywords to video titles. Use the following keyword matching rules: if the course name contains "Analytics" or "Algorithms", match videos whose titles contain words like "algorithm", "data", "code", or "software"; if the course name contains "Computing", match videos whose titles contain words like "code", "computing", "tech", or "programming"; if the course name contains "Data", match videos whose titles contain "data", "database", "code", or "analytics". For each match, record the specific keyword that caused the match.

Create an Excel file called Curriculum_Video_Map.xlsx in your workspace. The file must have two sheets.

The first sheet must be named Course_Videos and contain these columns in order: Course_Name, Course_Code, Video_ID, Video_Title, View_Count, Duration_Min, Relevance_Match. Course_Code should be the numeric course ID from the learning management system. Duration_Min must be the video duration in minutes rounded to one decimal place. Relevance_Match must be the keyword string that matched (for example "data" or "algorithm"). Sort the data by Course_Name ascending, then by View_Count descending within each course. Each course should have between 2 and 3 video rows.

The second sheet must be named Summary and contain exactly three rows with these labels in the first column: Total_Courses_Mapped, Total_Videos_Recommended, and Avg_Views_Recommended. The second column of each row contains the corresponding numeric value. Total_Courses_Mapped is the number of distinct courses with at least one video match. Total_Videos_Recommended is the total number of rows in the Course_Videos sheet excluding the header. Avg_Views_Recommended is the average view count across all recommended videos, rounded to the nearest integer.

Create a page in the team knowledge base titled "Tech Course Video Resources". The page must have a section for each matched course listing the course name as a heading and the recommended video titles beneath it.
