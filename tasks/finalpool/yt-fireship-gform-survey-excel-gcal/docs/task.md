You are a developer community manager. You want to survey your community about their video preferences, analyze which programming topics get the most engagement on the Fireship channel, create an online survey form for the community, compile video statistics into a spreadsheet, and schedule a community call. The community manager at community@devclub.io has asked you to prepare this monthly engagement report.

Your workflow should proceed as follows.

First, search the video platform for Fireship videos related to JavaScript and TypeScript content. From those results and from a broader search of the channel, select the top 8 videos by view count covering topics such as JavaScript, TypeScript, React, AI and machine learning, systems programming, and DevOps. For each video, collect the video identifier, title, view count, like count, duration in seconds, publication date, and the primary topic tag.

Second, create a spreadsheet file named Community_Report.xlsx. In the first sheet named Top_Videos, include the following columns in order: Rank, Video_ID, Title, Views, Likes, Duration_Sec, Topic_Tags. Populate this sheet with one row per video, ranked from highest to lowest by view count, with Rank starting at 1. Also compute the engagement rate for each video as likes divided by views multiplied by 100, and include this as an additional column named Engagement_Rate. In a second sheet named Engagement_Analysis, include the following columns: Topic, Avg_Engagement_Rate, Total_Views, Video_Count. Populate it with one row per distinct topic, aggregating the videos by their Topic_Tags. There should be at least 4 topic rows.

Third, create an online survey form titled "Fireship Community Preference Survey". Add the following questions to the form. The first question should ask "Which Fireship topic interests you most?" as a single-choice radio question with these options: JavaScript, TypeScript, React, AI and ML, Systems and Rust, DevOps and Cloud, Other. The second question should ask "How often do you watch Fireship?" as a radio question with options: Daily, Weekly, Monthly, Rarely. The third question should ask "What format do you prefer?" as a radio question with options: Short under 5 minutes, Medium 5 to 15 minutes, Long over 15 minutes. The fourth question should ask "Your current role" as a radio question with options: Student, Junior Developer, Senior Developer, Engineering Manager, Other. The fifth question should ask "What topic should Fireship cover next?" as an open text question.

Fourth, check the shared calendar for any existing community events in April 2026. Then create a new calendar event titled "Community Standup" scheduled for April 1 2026 from 18:00 to 19:00 UTC.

Fifth, send an email to community@devclub.io. The subject should reference the monthly engagement report. The body should summarize the top video topics, mention the engagement rates found, provide the survey form identifier so members can access it, and note the community standup scheduled for April 1.

The configuration file in your workspace is named community_config.json and contains the target topics and report title. A report template named report_template.md explains the column formats, how engagement rate is calculated, and the ranking logic.

When all outputs are complete, claim the task as done.
