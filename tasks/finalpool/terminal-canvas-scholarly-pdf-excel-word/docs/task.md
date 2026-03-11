The curriculum review committee wants to evaluate how well course assignments align with current academic research in the field of applied analytics and algorithms. There is a PDF file called Curriculum_Review_Guidelines.pdf in the workspace that describes the review criteria and scoring methodology. There is also a file called review_template.md that outlines the expected structure of the final report. Please read both files first.

Connect to the learning management system and retrieve course information and assignment details for the two sections of the Applied Analytics and Algorithms course (course identifiers 1 and 2). For each assignment, note the assignment name, point value, and due date.

Search the academic literature database for papers related to applied analytics, algorithms, and data science education. Find at least four relevant papers that could inform the curriculum. For each paper, record the title, authors, publication year, and a relevance score from 1 to 10 based on how closely the paper's topic relates to the course assignments.

Write and run a Python script called alignment_scorer.py in the workspace. The script should read from two JSON files you create: assignments_data.json (containing the assignment details from both courses) and papers_data.json (containing the scholarly paper information). For each assignment, the script should find the most relevant paper and compute an alignment score from 0 to 100 based on keyword overlap between the assignment name and paper title and abstract. The script should output alignment_matrix.json with the results.

Create an Excel file called Curriculum_Research_Alignment.xlsx in the workspace with three sheets.

The first sheet should be called Course_Assignments with columns Course_ID, Course_Name, Assignment_Name, Points, and Due_Date. Include all twelve assignments from both courses sorted by Course_ID then by Points ascending. Format the due dates as YYYY-MM-DD strings or leave blank if there is no due date.

The second sheet should be called Related_Papers with columns Title, Authors (as a comma-separated string of author names), Year, and Relevance_Score (an integer from 1 to 10). Include at least four papers sorted by Relevance_Score descending.

The third sheet should be called Alignment_Matrix with columns Assignment_Name, Matched_Paper (the title of the best-matching paper), and Alignment_Score (0 to 100). Include all twelve assignments sorted by Alignment_Score descending.

Create a Word document called Curriculum_Review_Report.docx in the workspace. The report should have a title, an executive summary section discussing the overall alignment between the curriculum and current research, a section describing each course and its assignments, a section summarizing the relevant papers found, a section presenting the alignment analysis results, and a conclusion with recommendations for curriculum improvement.
