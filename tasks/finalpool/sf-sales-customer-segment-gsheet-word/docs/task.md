You are a sales strategy analyst. Your task is to analyze customer segment performance from the sales data warehouse and produce a segment analysis report.

First, query the Snowflake sales data warehouse to retrieve metrics for each customer segment. Join the CUSTOMERS table with the ORDERS table on CUSTOMER_ID. Group by the SEGMENT column and calculate for each segment: the number of distinct customers, the total number of orders, and the total revenue (sum of TOTAL_AMOUNT). The four segments are: Consumer, Enterprise, Government, and SMB.

Next, create a Google Sheet titled "Customer Segment Analysis" with the following columns: Segment, Customer_Count, Order_Count, Total_Revenue, Revenue_Pct. The Revenue_Pct column should show each segment's percentage of total revenue (rounded to 2 decimal places). Order the rows by Total_Revenue descending. The sheet must have 4 data rows (one per segment) plus a header row.

Then, create a Word document called Customer_Segment_Report.docx in the workspace. The document must include: a heading "Customer Segment Analysis Report", an introduction paragraph summarizing the analysis scope, a table with the segment data (Segment, Customer_Count, Order_Count, Total_Revenue), and a "Recommendations" section heading followed by at least two recommendations based on the segment data.

Finally, email the report to sales-strategy@company.example.com from analytics@company.example.com with the subject "Customer Segment Analysis Report". The email body should summarize which segment generates the most revenue and which has the most customers.

The Segment_Strategy.pdf file in your workspace describes each customer segment and the strategic goals.
