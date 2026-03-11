I need help with a arxiv citation analysis. There is external benchmark data available that I need you to fetch the data from http://localhost:30322/api/data.json and extract the relevant metrics.

Then search for relevant academic papers on the topic.

Use the terminal to create and run a Python script called arxiv_citation_processor.py in the workspace that reads the collected data from JSON files you create, performs the analysis, and outputs arxiv_citation_results.json.

Create an Excel file called Citation_Network_Report.xlsx with three sheets. The first sheet Data_Analysis should contain the main comparison data with relevant columns. The second sheet Metrics should summarize key metrics. The third sheet Recommendations should list actionable items.

The Data_Analysis sheet should include columns for the primary dimension (such as department, product, region, or topic), our internal metric values, the external benchmark values, and the gap or difference between them. Sort the data alphabetically by the primary dimension. The Metrics sheet should have two columns Metric and Value summarizing total counts, averages, and key statistics. The Recommendations sheet should list priority actions based on the gap analysis. Create a Notion page titled "Arxiv Citation Dashboard" with a summary of the analysis.
