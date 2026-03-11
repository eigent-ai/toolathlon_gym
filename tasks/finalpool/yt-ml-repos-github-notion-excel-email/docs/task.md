You are a researcher on an ML team. Your principal investigator has asked you to catalog the curated ML technology videos from a channel called ML Tech Reviews on the video platform. This channel has a dedicated playlist of 7 videos, each covering a specific open-source machine learning project with a corresponding code repository. You need to catalog these videos, cross-reference them with related research papers from your local paper library, build a knowledge base page for the team, compile an Excel research tracker, and send a summary email.

Your workflow should proceed as follows.

First, retrieve the ML Tech Reviews playlist from the video platform. Get all items in the playlist. For each of the 7 videos, fetch the full details including the title, description, tags, publication date, and view count. From each video description, extract any repository link that points to a code hosting service. Identify the primary ML topic or technique that the video covers, such as Flash Attention, LoRA, Diffusion Models, RLHF, Mixture of Experts, Quantization, or Vector Databases, based on the title and tags.

Second, search your local paper library for research papers related to each of the 7 ML topics you identified. For each topic, retrieve the paper details including the paper identifier, title, authors, and publication date.

Third, create an Excel file named ML_Research_Tracker.xlsx. Create a sheet named Videos with these columns in order: Video_ID, Title, Topic, GitHub_URL, Published_Date, View_Count. Populate it with one row for each of the 7 videos. Create a second sheet named Papers with these columns: ArXiv_ID, Title, Authors, Published, Topic, Related_Video_ID. Populate it with one row per paper found, linking each paper to its related video by the video identifier. Create a third sheet named Summary with these columns: Topic, Video_Count, Paper_Count, GitHub_Repos_Count. Populate it with one row per topic, summarizing the counts.

Fourth, create a new page in the team knowledge base titled "ML Tech Research Hub". Add an introductory paragraph describing the purpose of the page and the channel being cataloged. Then create a database within the knowledge base titled "Research Items" with the following properties: Name as the title field, Type as a select field with options Video and Paper, Topic as a text field, URL as a text field, and Status as a select field with options New, In Review, and Archived. Add an entry for each of the 7 videos and for each paper you found.

Fifth, send an email to research@lab.edu. The subject should reference the ML research catalog. The body should summarize the number of videos cataloged, the number of papers found, the topics covered, and mention that the full details are in ML_Research_Tracker.xlsx and in the team knowledge base.

The research configuration file in your workspace is named research_config.md and explains the cataloging approach. A topic mapping file named topic_mapping.json lists the 7 expected ML topics to use as reference.

When all outputs are complete, claim the task as done.
