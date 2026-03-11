You are a research assistant preparing a literature review on transformer architectures in natural language processing. Your goal is to collect papers from multiple academic sources, analyze them, organize them in a knowledge base, and produce a comprehensive review document.

Start by searching the scholarly database for papers related to "transformer" and "attention mechanism". Retrieve all available papers and note their titles, authors, publication years, and journal references.

Next, search the arxiv repository for papers about "transformer" and "neural network". Download and read through the abstracts of the papers you find to understand what each paper covers.

Write and run a Python analysis script. The script should take the collected paper data and categorize each paper into one of these methodology categories: "Architecture Design" for papers proposing new model architectures, "Training Methods" for papers about training techniques or optimization, "Applications" for papers applying transformers to specific tasks, and "Survey" for papers that review or survey the field. Assign categories based on keywords in the title and abstract. The script should also identify which papers appear in both databases (overlap analysis by matching paper IDs).

Create a database in the knowledge base titled "Research Paper Tracker" with properties for Title (title type), Paper_ID (rich_text), Authors (rich_text), Year (number), Category (select with options Architecture Design, Training Methods, Applications, Survey), Source (select with options Scholarly, Arxiv, Both), and Abstract_Summary (rich_text). Add a page entry for each unique paper found across both databases.

Create a Word document called Transformer_Literature_Review.docx in the workspace. The document should have a title "Literature Review: Transformer Architectures in NLP", followed by an introduction section explaining the scope of the review. Then include a section for each methodology category listing the papers in that category with their titles, authors, year, and a brief description from the abstract. End with a conclusion section summarizing the state of the field and identifying research gaps.

Create an Excel file called Research_Paper_Analysis.xlsx in the workspace with three sheets. The first sheet "Paper_Catalog" should have columns Paper_ID, Title, Authors, Year, Source (Scholarly, Arxiv, or Both), and Category. The second sheet "Method_Comparison" should have columns Category, Paper_Count, Avg_Year, and Key_Papers (listing titles of papers in that category). The third sheet "Citation_Matrix" should list all unique papers with columns Paper_ID, Title, In_Scholarly (Yes or No), In_Arxiv (Yes or No), and Overlap (Yes if in both, No otherwise).

Your workspace contains review_guidelines.json with category definitions and lit_review_template.md with formatting guidance.
