You are an inventory manager responsible for monitoring product stock levels and coordinating restocking activities for an online store. Your goal is to analyze the current product inventory, forecast demand, generate reports, and ensure timely restock scheduling.

Start by reading the Inventory_Policy.pdf in your workspace, which describes the reorder thresholds and lead time expectations. Also review the warehouse_config.json file that contains warehouse capacity limits and supplier contact information.

Query the e-commerce platform to retrieve the complete product catalog. For each product, gather the product name, category, regular price, stock quantity, stock status, and total sales count. You will use this data to assess inventory health and compute reorder priorities.

Write a Python script called demand_forecast.py in your workspace and execute it using command-line tools. The script should compute a simple demand velocity metric for each product by dividing total sales by an assumed 180-day selling period to get daily sales rate. Then calculate days of supply by dividing current stock quantity by the daily sales rate (use 999 for products with zero sales rate). Determine a reorder point for each product as 14 times the daily sales rate (representing a 14-day lead time buffer). Flag products as Critical urgency if their current stock is at or below the reorder point and they are not out of stock, flag out-of-stock products as Out_of_Stock urgency, and flag all others as Normal.

Create an Excel workbook called Inventory_Lifecycle_Report.xlsx in your workspace with four sheets.

The first sheet should be named Product_Inventory and contain columns for product_name, category, price, stock_qty, stock_status, total_sales, and days_of_supply. Include one row for every product in the catalog, sorted by days_of_supply ascending so the most urgent items appear first.

The second sheet should be named Reorder_Alerts and contain columns for product_name, current_stock, reorder_point, and urgency. Include only the products that have Critical or Out_of_Stock urgency, sorted by urgency with Out_of_Stock items first.

The third sheet should be named Category_Summary and contain columns for category, product_count, avg_stock, and total_value. Total value should be the sum of price times stock quantity for each product in the category. Include one row per product category.

The fourth sheet should be named Restock_Schedule and contain columns for product_name, reorder_date, quantity, and supplier. For each Critical or Out_of_Stock product, set the reorder date to March 10, 2026. The quantity to order should be the reorder point minus current stock (minimum 1 unit). The supplier should be "Primary Supplier" for all items.

Publish the Category_Summary data to the shared spreadsheet system so the team can view real-time inventory status. Create a spreadsheet titled "Inventory Dashboard" with a sheet containing the category summary data.

Schedule a restock review meeting on the shared calendar for March 11, 2026 at 10:00 AM lasting one hour. The event summary should be "Inventory Restock Review Meeting" and the description should mention the number of critical items identified.

Send an email to purchasing@company.com with the subject "Critical Inventory Alert - Restock Required" summarizing the number of out-of-stock and critical products, along with the top three most urgent items that need immediate restocking.
