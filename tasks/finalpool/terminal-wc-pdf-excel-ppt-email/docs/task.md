You are an operations analyst handling a product recall situation for an online store. A supplier has notified your team about potential defects in certain product lines, and you need to assess the full impact on orders, customers, and revenue.

Start by reading the recall_notice.pdf in your workspace. This document from the supplier lists the affected product names and details about the defects discovered. Also read the customer_communication_template.txt file, which contains a template for notifying affected customers, and the recall_procedure.md file, which outlines your standard operating procedure for handling recalls.

Search the e-commerce platform for the products mentioned in the recall notice. You need to find those products by name and retrieve their details including product name, SKU, price, and stock quantity. Then look up all orders that contain any of those recalled products. For each matching order, gather the order ID, billing email, order date, order total, and the quantity and line total for the recalled product in that order.

Write a Python script called recall_analysis.py in your workspace and execute it. The script should compute the following metrics from the data you gathered. For each recalled product, calculate the total number of units sold across all orders, the number of distinct orders affected, and the total revenue at risk which is the sum of line totals for that product. Also compute the overall totals across all recalled products for units sold, orders affected, and revenue at risk. Count the number of unique customers affected based on distinct billing email addresses. The script should output its results to recall_impact.json in your workspace.

Write a second Python script called customer_impact.py and execute it. This script should generate a per-customer impact summary. For each unique customer email, list the recalled products they purchased, the order dates, and the total amount at risk for that customer. Output the results to customer_impact.json in your workspace.

Create an Excel workbook called Recall_Impact_Assessment.xlsx in your workspace with four sheets.

The first sheet should be named Affected_Products with columns product_name, sku, units_sold, orders_affected, and revenue_at_risk. Include one row per recalled product, sorted by revenue_at_risk descending.

The second sheet should be named Customer_Impact with columns customer_email, products_affected, total_amount, and order_dates. Include one row per affected customer, sorted by total_amount descending. The products_affected column should contain the names of recalled products that customer ordered, separated by semicolons if multiple. The order_dates column should contain the dates formatted as YYYY-MM-DD, separated by semicolons if multiple.

The third sheet should be named Financial_Summary with columns metric and value. Include the following rows: Total Units Affected, Total Orders Affected, Total Revenue at Risk, Unique Customers Affected, and Average Revenue per Order.

The fourth sheet should be named Timeline with columns action, deadline, responsible, and status. Include at least four rows covering the key recall actions: Identify Affected Orders with deadline March 8 2026 assigned to Operations with status Complete, Notify Customers with deadline March 10 2026 assigned to Customer Service with status Pending, Process Returns with deadline March 17 2026 assigned to Warehouse with status Pending, and Financial Reconciliation with deadline March 21 2026 assigned to Finance with status Pending.

Create a PowerPoint presentation called Recall_Briefing.pptx in your workspace with five slides. The first slide should be a title slide. If the total revenue at risk exceeds $5000, the title should read "Major Recall Impact Assessment" and otherwise it should read "Minor Recall Impact Assessment". Include a subtitle with the current date. The second slide should cover Scope of Recall listing the affected product names and the defect type from the recall notice. The third slide should present the Financial Impact showing total units affected, total orders affected, total revenue at risk, and unique customers affected. The fourth slide should outline the Customer Communication Plan describing how affected customers will be notified and what remediation options are available. The fifth slide should show the Remediation Timeline with the key milestones from the Timeline sheet.

Send an email to operations@company.com with subject "Product Recall Alert - Impact Summary" including a summary of which products are recalled, how many orders and customers are affected, and the total revenue at risk.

Send an email to finance@company.com with subject "Recall Financial Impact Report" including the total revenue at risk, the number of affected orders, and the average revenue per affected order.

Send an email to legal@company.com with subject "Recall Customer Communication Plan" including the total number of affected customers and a brief description of the planned customer notification approach.
