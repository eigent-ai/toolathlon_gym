You are the VP of Customer Experience preparing a quarterly quality review that combines e-commerce performance data with support center metrics. The goal is to understand how product-related issues in the online store correlate with support ticket patterns, and present the findings in a board-ready format.

Begin by visiting the customer satisfaction portal at http://localhost:30239 to review the current satisfaction benchmarks and targets. The main page shows the overall satisfaction target, response time target, resolution rate target, and NPS target. Navigate to the trends page at http://localhost:30239/trends.html to see monthly CSAT trends and competitive benchmarks.

Next, connect to the e-commerce platform and retrieve all order data. Focus on identifying orders with issues by looking at orders that have a status of refunded or cancelled, as these represent problematic transactions. Group the orders by the product categories involved (you can determine the category from the product details in each order's line items) and calculate the total number of orders and the number of issue orders (refunded or cancelled) for each category. Compute an issue rate as the percentage of orders with issues in each category.

Then query the support center data warehouse for ticket performance metrics. For each priority level (High, Medium, Low), calculate the total ticket count, average response time in hours, average customer satisfaction rating, and the resolution rate. Compare these metrics against the targets from the satisfaction portal.

For the cross-reference analysis, look at the overall patterns. Determine which product categories have the highest issue rates from the e-commerce data, and examine whether the support center metrics (particularly response times and satisfaction scores) vary by issue type. This provides insight into whether high-issue product categories are also causing support quality challenges.

Create an Excel file called CX_Quality_Review.xlsx in your workspace with four sheets. The first sheet should be called "Order Issues" with columns for Category, Total_Orders, Issue_Orders, and Issue_Rate_Pct. Include all product categories found in the order data.

The second sheet should be called "Support Metrics" with columns for Priority, Ticket_Count, Avg_Response_Time_Hours, Avg_Satisfaction, Resolution_Rate_Pct, Response_Target_Hours (from the portal), and Meets_Response_Target (Yes or No). Include rows for each priority level.

The third sheet should be called "Cross Reference" with columns for Issue_Type, Ticket_Count, Avg_Response_Time, Avg_Satisfaction. Include all issue types from the support data.

The fourth sheet should be called "Executive Summary" with columns for Metric and Value. Include rows for total orders analyzed, overall issue rate, total support tickets, average response time across all priorities, average customer satisfaction, and whether the overall targets are being met.

Finally, create a PowerPoint presentation called Quality_Review.pptx in your workspace with at least six slides. The presentation should include a title slide, an overview of the satisfaction benchmarks and targets, a summary of e-commerce order issues by category, support center performance by priority level, the cross-reference findings, and recommendations for improving customer experience quality.

When you have completed all tasks, call claim_done.
