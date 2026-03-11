I need to build a comprehensive research knowledge base for our team studying large language models. Start by searching for recent scholarly papers on topics like "large language models", "prompt engineering", and "in-context learning". Find at least 5 relevant papers.

Then use the paper repository to download and read the full content of the most relevant papers. Analyze their LaTeX source when available to extract detailed methodology sections.

Use the terminal to create and run a Python script called research_synthesizer.py in the workspace that reads papers_metadata.json and paper_contents.json (create both first), extracts key methods, creates a citation network map, calculates relevance scores, and outputs research_synthesis.json.

Create an Excel file called Research_Knowledge_Base.xlsx with three sheets. The first sheet Paper_Catalog should have columns Paper_ID, Title, Authors, Year, Category, and Citation_Count, sorted by Citation_Count descending. The second sheet Method_Comparison should have columns Method_Name, Paper_Source, Key_Innovation, Benchmark_Result, and Applicability ("High", "Medium", "Low"). The third sheet Research_Gaps should have Gap_Area, Current_State, Opportunity, and Priority ("Critical", "Important", "Nice-to-have") columns with at least 4 identified gaps.

Create a Notion page titled "LLM Research Hub" with a heading "Large Language Model Research Dashboard". Add paragraphs covering research landscape overview, key papers summary, methodology comparison highlights, and identified research gaps with recommendations for future work.
