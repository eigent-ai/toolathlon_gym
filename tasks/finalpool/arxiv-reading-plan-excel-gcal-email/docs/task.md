You are a research coordinator for an LLM agent research reading group. Your workspace contains paper_ids.txt with a list of eight arXiv paper IDs and Reading_Guidelines.md describing the reading group format and discussion expectations.

Your task is to create a structured reading plan for the group. Follow these steps exactly.

Step 1: For each paper ID listed in paper_ids.txt, retrieve the paper metadata from the arXiv local tools. The paper IDs are: 2301.13379, 2302.01560, 2303.12528, 2305.10403, 2308.12950, 2309.17453, 2201.11903, and 2310.06825.

Step 2: Create an Excel file called Reading_Plan.xlsx in your workspace with two sheets. The first sheet must be named Papers and contain exactly eight rows (one per paper) with these columns: ArXiv_ID, Title, Authors, Published_Date, Category, Abstract_Summary (first 100 characters of the abstract), Assigned_Session (a number from 1 to 8 assigned in the order the papers appear in paper_ids.txt). The second sheet must be named Schedule and contain exactly eight rows (one per reading session) with these columns: Session_Number, Session_Date, Paper_Count, Topics_Covered. Session 1 starts on the Monday of the launch week and each subsequent session is one week later. Each session covers one paper. Topics_Covered should be the abbreviated title or topic area of that session's paper.

Step 3: Create eight Google Calendar events, one for each reading session. Each event title must follow the pattern "Reading Session N: [abbreviated paper title]" where N is the session number. Schedule each event on the corresponding Monday starting from the Monday of the launch week, at 10:00 to 11:30 UTC. Include the full paper title and arXiv ID in the event description.

Step 4: Send an email from coordinator@lab.example.com to reading-group@lab.example.com. The subject must contain "LLM Agent Research Reading Plan". The body must mention the total number of papers, the date range covered by the reading sessions, and the names or topics of at least three of the eight papers.

Complete all four steps and call claim_done when finished.
