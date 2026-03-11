We suspect that certain product categories in our online store are generating more customer support tickets than others. I need you to cross-reference our support ticket database with our e-commerce order data to identify product quality patterns.

Start by querying the support ticket system for all tickets grouped by priority level (High, Medium, Low). Get the count of tickets per priority and the average response time in hours for each priority level.

Next, query the e-commerce platform for order data. Get a breakdown of orders by status (completed, processing, refunded, cancelled, etc.) with counts for each status. Also retrieve the product categories and the number of products in each category.

Create and run a Python script called defect_correlation.py in the workspace. The script should read both datasets from JSON files you create (support_tickets.json and order_data.json), correlate ticket volumes with order volumes to identify potential quality issues, compute a defect rate estimate (tickets per 100 orders) for each priority level, and output quality_analysis_results.json.

Create an Excel file called Product_Quality_Report.xlsx with three sheets. The first sheet Ticket_by_Priority should have columns Priority, Ticket_Count, Avg_Response_Hours (rounded to 2 decimals), and Pct_of_Total (percentage of all tickets, rounded to 1 decimal). Sort by Ticket_Count descending.

The second sheet Order_Status_Breakdown should have columns Status, Order_Count, Pct_of_Orders (rounded to 1 decimal), and Quality_Flag (set to "Review" for refunded or cancelled orders, "OK" for others).

The third sheet Quality_Action_Plan should have columns Issue, Severity (High, Medium, or Low), Owner, Deadline, and Action_Item. Include at least 5 action items based on the analysis findings, such as addressing high-priority ticket response times, investigating refund patterns, and improving product descriptions for problematic categories.

Send two emails. First, send an email to quality-team@company.com with subject "Product Quality Analysis Report Ready" summarizing the key findings including total ticket count, highest volume priority level, and defect rate. Second, send an email to operations@company.com with subject "Quality Review Meeting Required" describing the top issues that need immediate attention.

Schedule two events on the shared calendar. First, a "Quality Review Meeting" on March 19, 2026 from 10:00 to 11:30 with description mentioning the key findings. Second, a "Quality Improvement Planning" session on March 21, 2026 from 14:00 to 16:00 with description listing the action items from the Quality_Action_Plan.
