The customer service leadership team has requested a cross-platform quality audit comparing support ticket response patterns with e-commerce order complaint data. The goal is to understand whether product categories with higher problem order rates (refunded, cancelled, or failed orders) are correlated with higher volumes of support tickets at elevated priority levels.

Start by reviewing the quality framework document and configuration file in the workspace to understand the audit thresholds and who should receive the final report.

Pull support ticket data from the company data warehouse, focusing on ticket counts, average response times, and average satisfaction scores broken down by priority level (High, Medium, Low). Also pull e-commerce order data to identify problem orders, which are orders with a status of refunded, cancelled, or failed. Calculate the problem order rate for each product category as the percentage of total orders in that category that are problem orders.

Run a correlation analysis between support ticket priority distributions and product category problem rates. The analysis should compute a simple cross-reference showing which product categories have above-average problem rates and how ticket volume distributes across priorities.

Create a cloud spreadsheet called "Support Quality Audit" with three sheets. The first sheet "Ticket_Priority_Summary" should have columns Priority, Ticket_Count, Avg_Response_Hours (rounded to 2 decimals), and Avg_Satisfaction (rounded to 2 decimals), sorted by Priority alphabetically. The second sheet "Product_Problem_Rates" should have columns Category, Total_Orders, Problem_Orders, Problem_Rate_Pct (rounded to 1 decimal), sorted by Category alphabetically. The third sheet "Audit_Summary" should have columns Metric and Value containing: Total_Tickets (sum of all tickets), Total_WC_Orders (total e-commerce orders), Overall_Problem_Rate_Pct (rounded to 1 decimal), Highest_Problem_Category (category name with highest problem rate), High_Priority_Pct (percentage of tickets that are High priority rounded to 1 decimal).

Also produce an Excel file called Support_Quality_Audit.xlsx with the same three sheets and identical data as the cloud spreadsheet.

Write a Word document called Support_Audit_Report.docx that provides an executive summary of the audit findings, discusses the relationship between product problem rates and support ticket patterns, identifies the product category with the most quality issues, and offers recommendations for improving customer service response times.

Finally, email the audit report to cs_leadership@company.com with the subject "Q1 Support Quality Audit Results" and include a brief overview of the key findings in the email body.
