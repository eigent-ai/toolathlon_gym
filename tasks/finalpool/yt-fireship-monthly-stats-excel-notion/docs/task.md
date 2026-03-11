You are a tech content strategist responsible for tracking your team's learning through a popular programming and technology video channel called Fireship. Your task is to analyze the channel's publishing history and performance metrics stored in the team's video database and produce a structured report.

Start by querying the video database to retrieve all videos published by the Fireship channel. For each video, you have access to the publication date, view count, and like count.

Compute a monthly breakdown of the channel's activity. For each calendar month that had at least one published video, calculate the number of videos published, the average view count rounded to zero decimal places, the average like count rounded to zero decimal places, and the total view count for that month.

Create a spreadsheet file called Fireship_Monthly_Stats.xlsx in your workspace. This file must contain two sheets.

The first sheet must be named Monthly_Stats. It should have one row per month with the following columns in order: Month (formatted as YYYY-MM), Video_Count, Avg_Views, Avg_Likes, and Total_Views. Sort the rows by Month in ascending chronological order.

The second sheet must be named Summary. It should have exactly two columns named Label and Value, with the following rows in order: Total_Videos (the total number of videos across all months), Total_Months_Active (how many distinct months had at least one video), Peak_Month (the YYYY-MM month string that had the highest Video_Count), Peak_Month_Videos (the video count for that peak month), Best_Avg_Views_Month (the YYYY-MM month string that had the highest Avg_Views), and Best_Avg_Views (the average view count for that best month as a rounded integer).

After creating the spreadsheet, create a page in the team knowledge base titled exactly "Fireship Channel Analysis 2024-2025". The page content should be a written paragraph summarizing the key findings: total video count, number of active months, the peak publishing month, and the month with the best average views.

Finally, send an email to analytics@company.com with the subject line "Fireship Channel Analysis Complete". The email body should briefly summarize the main findings from your analysis.
