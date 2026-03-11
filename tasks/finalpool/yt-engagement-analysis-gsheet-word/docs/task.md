Our social media research team wants a comprehensive engagement analysis of all available videos from the Fireship tech channel. Engagement rate is defined as the number of likes divided by the number of views, expressed as a percentage.

Retrieve all available Fireship videos from the video database. For each video, compute the engagement rate by dividing like_count by view_count and multiplying by 100, rounded to three decimal places. Also extract the publication month in YYYY-MM format and convert the duration from seconds to an integer value.

Create a cloud spreadsheet called "Fireship Engagement Analysis". The spreadsheet must have two sheets.

The first sheet must be named Engagement_Data and contain these columns in order: Video_ID, Title, Published_Month, Duration_Sec, View_Count, Like_Count, Engagement_Rate_Pct. Each row represents one Fireship video. Sort all rows by Engagement_Rate_Pct in descending order (highest engagement first). The Published_Month column must be in YYYY-MM format (for example 2024-07). Duration_Sec must be stored as an integer. Engagement_Rate_Pct must be rounded to 3 decimal places.

The second sheet must be named Monthly_Summary and contain these columns: Month, Video_Count, Avg_Engagement_Rate, Top_Video_Title. Each row represents one calendar month. Month must be in YYYY-MM format. Video_Count is the number of Fireship videos published in that month. Avg_Engagement_Rate is the average of Engagement_Rate_Pct for all videos in that month, rounded to 3 decimal places. Top_Video_Title is the title of the video with the single highest engagement rate in that month. Sort rows by Month in ascending order.

Write a Word document called Engagement_Analysis_Report.docx in your workspace. The document must contain these five sections with their exact headings: Overview, Methodology, Key Findings, Monthly Trends, and Conclusions. The Key Findings section must name and include the engagement rate percentage for the top three most engaging Fireship videos. The Methodology section must state that engagement rate equals like_count divided by view_count multiplied by 100.

Send an email to research@company.com with the subject line "Fireship YouTube Engagement Analysis". The email body must summarize the total number of videos analyzed and reference at least one of the top engaging videos by name.
