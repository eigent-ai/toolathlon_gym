Technology Overview Creation Guide

Mapping Videos to Academic Research
For each AI-related video, extract the core technology keyword from the title and description. Use this keyword to search the academic paper system. A strong match is when the paper title contains the same technology term (e.g., video about transformers maps to papers about attention mechanisms or transformer architectures).

Technology Trend Classification
Emerging: paper published within the last 12 months and has fewer than 100 citations, or technology is very new (e.g., announced in 2024).
Growing: paper is 1 to 3 years old and has between 100 and 500 citations, indicating active community adoption.
Established: paper is more than 3 years old and has more than 500 citations, indicating broad community adoption.

Presentation Structure
The presentation must have at least 5 slides. Slide 1 is the title slide. Slide 2 covers the most viewed video content. Slide 3 covers the academic research highlights. Slide 4 presents the technology landscape map. Slide 5 gives key insights and recommendations for the research group.

Spreadsheet Column Requirements
Videos sheet: Video_ID (unique identifier), Title (full video title), Topic (one of: LLM, Code AI, Generative AI, Transformers, Tools), View_Count (integer), Published_Date (YYYY-MM-DD), Key_Technologies (comma-separated list).
Papers sheet: Paper_Title, Authors (comma-separated), Year (integer), Venue (conference or journal name), Citations (integer), Related_Video_Topic.
Technology_Map sheet: Technology (name), Video_Mentions (integer count), Paper_Count (integer), Trend_Status (Emerging / Growing / Established).
