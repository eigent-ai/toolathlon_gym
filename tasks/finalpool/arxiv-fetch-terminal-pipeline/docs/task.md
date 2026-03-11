A research engineer needs to build a paper analysis pipeline for a team studying federated learning. Please complete the following steps.

First, search the arxiv database for papers about federated learning. You should find around four relevant papers covering topics such as communication-efficient learning, non-IID data handling, personalized federated learning, and heterogeneous optimization. Retrieve the full details for each paper including title, authors, and abstract.

Second, supplement this information by searching for citation counts and venue information for each of the papers you found. Record the citation count and venue for each paper.

Third, create a JSON file called paper_data.json in the workspace directory containing an array of objects, one per relevant paper. Each object should have the fields: id (the arxiv paper ID), title, authors (as a list of name strings), citations (the citation count as a number), and venue. Only include the federated learning papers, not any unrelated papers.

Fourth, write a Python analysis script called analysis_pipeline.py in the workspace that reads paper_data.json and performs the following calculations: average citations across all papers, identifies the most cited paper, counts how many papers appear in each venue, and reports the total number of papers. The script should output its results to a file called analysis_results.json in the workspace, containing an object with keys average_citations, most_cited_paper (the title), papers_per_venue (an object mapping venue names to counts), and total_papers.

Fifth, run the analysis script to produce analysis_results.json.

Finally, create a text file called pipeline_report.txt in the workspace that summarizes the analysis findings in a few paragraphs. The report should mention the research topic, the papers found, key statistics from the analysis, and any notable observations about the federated learning research landscape.
