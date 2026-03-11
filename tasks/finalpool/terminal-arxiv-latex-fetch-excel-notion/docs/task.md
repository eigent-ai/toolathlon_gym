I am preparing to present at the International Conference on Machine Learning Methods. The conference schedule is available as a JSON endpoint at http://localhost:30412/api/conference.json. Please fetch the conference schedule data first.

Next, I need to review the research papers in our LaTeX paper archive. Search for papers related to machine learning, specifically about scaling laws, instruction tuning, and open-source language models. For each paper found, retrieve the full content including all section titles, abstracts, and key findings from the LaTeX source.

Create and run a Python script called conference_prep_builder.py in the workspace. The script should read the conference schedule from conference_schedule.json and the paper analysis data from paper_analysis.json (both files you create from the fetched data), cross-reference which papers are relevant to which conference sessions, extract word counts per section, and output conference_prep_results.json.

Create an Excel file called Conference_Prep_Tracker.xlsx with three sheets. The first sheet Paper_Sections should have columns Paper_ID, Paper_Title, Section_Title, and Section_Word_Count (approximate word count of each section). Include all sections from all relevant papers found. Sort by Paper_ID then section order.

The second sheet Conference_Schedule should have columns Session_ID, Session_Title, Date, Time, Room, and Related_Papers (comma-separated paper titles that match the session topic). The data comes from the conference JSON.

The third sheet Presentation_Notes should have columns Slide_Number (1 through at least 8), Topic, Key_Points (2-3 sentence summary), and Source_Paper. Create a logical presentation flow starting with introduction, covering each paper's main findings, and ending with a conclusion.

Finally, create a page in the knowledge base titled "Conference Prep Notes" with structured content. The page should include properties for Conference_Name (text), Presentation_Date (text showing the date), Status (select with value "In Progress"), and Paper_Count (number). Also add descriptive content blocks summarizing each paper's key contribution and how it relates to the conference themes.
