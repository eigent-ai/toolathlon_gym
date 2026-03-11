I need help with a sf wc reconcile analysis. There is external benchmark data available that I need you to visit http://localhost:30326 and extract the relevant metrics.

Then pull our internal data from the company data warehouse for comparison.

Use the terminal to create and run a Python script called sf_wc_reconcile_processor.py in the workspace that reads the collected data from JSON files you create, performs the analysis, and outputs sf_wc_reconcile_results.json.

Create an Excel file called Wc_Reconciliation_Report.xlsx with three sheets. The first sheet Data_Analysis should contain the main comparison data with relevant columns. The second sheet Metrics should summarize key metrics. The third sheet Recommendations should list actionable items.

The Data_Analysis sheet should include columns for the primary dimension (such as department, product, region, or topic), our internal metric values, the external benchmark values, and the gap or difference between them. Sort the data alphabetically by the primary dimension. The Metrics sheet should have two columns Metric and Value summarizing total counts, averages, and key statistics. The Recommendations sheet should list priority actions based on the gap analysis. Also create a Word document called Wc_Reconciliation_Analysis.docx with an executive summary, key findings, and recommendations sections.
