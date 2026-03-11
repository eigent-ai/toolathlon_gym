Our e-commerce marketing team wants to align product promotions with trending tech topics appearing in popular YouTube videos to time marketing campaigns around content our customers are already watching.

From the video database, retrieve all Fireship channel videos published from January 1, 2024 onwards. Select the top 10 videos by view count from that set. For each of the 10 videos, identify the main tech topic from the video title using these rules: if the title contains "DeepSeek" or "AI" or "OpenAI" or "GPT" or "Grok" or "Claude" or "vibe", the topic is "AI"; if the title contains "Linux", the topic is "Linux"; if the title contains "Windows", the topic is "Windows"; if the title contains "JavaScript" or "CSS" or "TypeScript" or "React" or "Node" or "Deno", the topic is "JavaScript/Web"; if the title contains "Python", the topic is "Python"; if the title contains "security" or "hack" or "Hackers" or "encrypted", the topic is "Security"; for all others, use "Tech/General".

Then retrieve all products from the online store. For each of the 10 videos, look for products whose name or description contains any keyword found in the video title (check for words like "laptop", "USB", "hub", "adapter", "TV", "monitor", "tablet", "watch", "headphone", "camera"). Record each video-product match with the specific keyword that triggered the match.

Create an Excel file called Marketing_Opportunity_Report.xlsx in your workspace with three sheets.

The first sheet must be named Video_Topics with these columns in order: Rank (1-10), Title, View_Count, Publish_Date (YYYY-MM-DD format), Main_Topic. Sort by Rank ascending.

The second sheet must be named Product_Matches with these columns: Video_Title, Product_ID, Product_Name, Product_Price, Match_Keyword. Include all matches found. If no product match exists for a video, omit that video from this sheet.

The third sheet must be named Summary with exactly three rows: the first row has label "Total_Videos_Analyzed" and the count of videos analyzed (10); the second row has label "Total_Product_Matches" and the total number of rows in Product_Matches; the third row has label "Most_Common_Topic" and the topic that appears most frequently across the top 10 videos.

Send an email to marketing@company.com with subject "Tech Video Marketing Opportunities". The email body must describe the top 3 video-product matches found, naming the video title and the matching product name for each.
