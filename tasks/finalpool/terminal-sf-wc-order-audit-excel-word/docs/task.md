You are a financial auditor responsible for reconciling sales data between the company's data warehouse and the online store. The company uses two separate systems to track orders. The data warehouse captures all order transactions across multiple regions, while the online store handles e-commerce operations with its own product catalog. Your job is to perform a thorough cross-system audit.

Start by reading the Audit_Procedures.pdf document in your workspace. It outlines the reconciliation methodology and the specific metrics you need to compute.

First, query the data warehouse to get a summary of all orders. You need to group orders by their status (Delivered, Shipped, Processing, Cancelled) and calculate the total count and total revenue for each status. Also compute the overall average order value across all orders, and the total number of distinct customers.

Next, query the online store system to retrieve all products and their details. Get the list of all orders from the store, including order totals and statuses. Also retrieve customer information from the store.

Now write and run a Python script called audit_analysis.py in your workspace. This script should read the data from both systems (you can hardcode the values you gathered) and compute the following: the total order count from the data warehouse, the total order count from the online store, the difference between them, the average order value from each system, and a category-level revenue breakdown from the data warehouse by ship mode (Economy, Express, Next Day, Standard).

Create an Excel workbook called Order_Audit_Report.xlsx in your workspace with four sheets.

The first sheet should be named DW_Summary and contain columns Status, Order_Count, and Total_Revenue. Include one row for each order status from the data warehouse: Cancelled, Delivered, Processing, and Shipped. Add a totals row at the bottom.

The second sheet should be named Store_Summary and contain columns Metric and Value. Include rows for Total Products (82 products in the store), Total Orders, Total Customers, and Average Order Value from the online store.

The third sheet should be named ShipMode_Breakdown and contain columns Ship_Mode, Order_Count, and Total_Revenue. Include rows for Economy, Express, Next Day, and Standard shipping modes from the data warehouse.

The fourth sheet should be named Reconciliation and contain columns Metric, DW_Value, Store_Value, and Difference. Include rows comparing Total Order Count, Average Order Value, and Total Revenue between the two systems. The Difference column should be the data warehouse value minus the store value.

Finally, create a Word document called Audit_Findings.docx in your workspace. The document should have a title "Order Reconciliation Audit Report". Include a section discussing the data warehouse summary with order counts and revenue by status. Include another section on the online store summary. Add a section on the ship mode breakdown showing how revenue distributes across shipping methods. End with a reconciliation findings section that highlights the key differences between the two systems and provides recommendations for alignment.
