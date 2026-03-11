I need help with a wc shipping analysis. There is external benchmark data available that I need you to fetch the data from http://localhost:30308/api/data.json and extract the relevant metrics.

Then check our online store for current product and order data.

Use the terminal to create and run a Python script called wc_shipping_processor.py in the workspace that reads the collected data from JSON files you create, performs the analysis, and outputs wc_shipping_results.json.

Create an Excel file called Shipping_Audit_Report.xlsx with three sheets. The first sheet Data_Analysis should contain the main comparison data with relevant columns. The second sheet Metrics should summarize key metrics. The third sheet Recommendations should list actionable items.

The Data_Analysis sheet should include columns for the primary dimension (such as department, product, region, or topic), our internal metric values, the external benchmark values, and the gap or difference between them. Sort the data alphabetically by the primary dimension. The Metrics sheet should have two columns Metric and Value summarizing total counts, averages, and key statistics. The Recommendations sheet should list priority actions based on the gap analysis. Also create a Word document called Shipping_Audit_Analysis.docx with an executive summary, key findings, and recommendations sections.
