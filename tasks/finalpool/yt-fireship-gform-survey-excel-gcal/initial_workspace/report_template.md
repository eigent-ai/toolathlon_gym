Community Report Template

Top_Videos Sheet Format
Columns in order: Rank, Video_ID, Title, Views, Likes, Duration_Sec, Topic_Tags, Engagement_Rate
Rank: Integer starting at 1, sorted by Views descending.
Engagement_Rate: Calculated as (Likes / Views) * 100, rounded to 2 decimal places.
Topic_Tags: The primary programming topic of the video (e.g., JavaScript, TypeScript, React, AI/ML).

Engagement_Analysis Sheet Format
Columns in order: Topic, Avg_Engagement_Rate, Total_Views, Video_Count
One row per distinct topic from Top_Videos.
Avg_Engagement_Rate: Average of Engagement_Rate values for all videos in that topic.
Total_Views: Sum of Views for all videos in that topic.
Video_Count: Number of videos in that topic.

Ranking Logic
Sort all videos by Views in descending order before assigning ranks.
Use the View count from the video platform as the primary sort key.

Survey Questions
The survey should have exactly 5 questions covering:
1. Preferred topic (radio)
2. Viewing frequency (radio)
3. Preferred video format/length (radio)
4. Current professional role (radio)
5. Open suggestion for future topics (text)
