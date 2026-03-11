The finance team needs a cross-system revenue reconciliation between the e-commerce storefront and the enterprise data warehouse. There is a PDF file called Reconciliation_Guidelines.pdf in the workspace that describes the audit procedures and acceptable variance thresholds. There is also a JSON file called audit_thresholds.json that defines the tolerance levels for flagging discrepancies. Please read both files to understand the audit criteria.

First, pull order and revenue data from the e-commerce platform. Get a summary of orders grouped by status, including the count of orders and total revenue for each status. Focus particularly on completed and processing orders as these represent confirmed revenue. Also calculate the average order value for these confirmed orders.

Next, query the enterprise data warehouse for order data. Get a summary of orders grouped by shipping method, including order count and total revenue for each. Also get a breakdown by customer region. Calculate the average order value across all warehouse orders.

Write and run a Python script called reconciliation_engine.py in the workspace. The script should read from two JSON files you create (wc_revenue_data.json and sf_revenue_data.json containing the data from both systems). The script should compute the following cross-system comparison metrics: total order count from each system, total revenue from each system, average order value from each system, and the percentage variance between the two systems for each of these metrics. It should output reconciliation_results.json.

Create an Excel file called Revenue_Reconciliation.xlsx in the workspace with four sheets.

The first sheet should be called WC_Summary with columns Status, Order_Count, and Total_Revenue. Include all order statuses from the e-commerce platform sorted by Total_Revenue descending. Add a total row at the bottom summing confirmed orders only (completed plus processing).

The second sheet should be called SF_Summary with columns Region, Order_Count, and Total_Revenue. Include all five regions from the data warehouse sorted by Total_Revenue descending. Add a total row at the bottom. Also include a second section below with a blank row separator showing the shipping method breakdown with columns Ship_Mode, Order_Count, and Total_Revenue.

The third sheet should be called Cross_Audit with columns Source, Metric, WC_Value, SF_Value, Variance_Pct (the percentage difference calculated as the absolute difference divided by the average of the two values times 100, rounded to one decimal place), and Flag (set to "REVIEW" if variance exceeds 50 percent, otherwise "OK"). The metrics to compare are Total_Orders, Total_Revenue, and Avg_Order_Value.

The fourth sheet should be called Recommendations with columns Finding_Number (1 through 5), Category, Finding, and Recommended_Action. Provide five findings based on the reconciliation results, such as the difference in scale between the two systems, the revenue gap, pricing strategy observations, and suggestions for system alignment.

Create a PowerPoint presentation called Reconciliation_Presentation.pptx in the workspace with at least five slides. The first slide should be a title slide with "Revenue Reconciliation Audit Report". The second slide should summarize the e-commerce platform data. The third slide should summarize the data warehouse figures. The fourth slide should present the cross-audit comparison with specific variance percentages. The fifth slide should list the key findings and recommended next steps.
