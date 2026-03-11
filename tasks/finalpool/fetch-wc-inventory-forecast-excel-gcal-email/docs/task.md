I need to forecast our inventory needs and plan restocking. There is a supplier catalog API at http://localhost:30306/api/supplier_catalog.json with lead times and minimum order quantities for our suppliers. Please fetch that data.

Then check our online store for current product stock levels, sales figures, and product details.

Use the terminal to create and run a Python script called inventory_forecaster.py in the workspace that reads supplier_data.json and product_stock.json (create both), calculates daily sales rates and days of remaining stock for each product, and outputs restock_plan.json. Daily rate is Total_Sales divided by 90 (assuming 90-day sales window). Days remaining is Current_Stock divided by daily rate. A product needs restock if days remaining is less than 30.

Create an Excel file called Inventory_Forecast_Report.xlsx with three sheets. The first sheet Stock_Status should have columns Product, Current_Stock, Total_Sales, Daily_Rate (round to 2 decimals), Days_Remaining (round to 1 decimal), and Needs_Restock ("Yes" if under 30 days, "No" otherwise). Sort by Product name alphabetically.

The second sheet Supplier_Info should list each supplier with columns Supplier, Lead_Time_Days, Min_Order_Qty, and Reliability_Score.

The third sheet Restock_Summary should have Metric and Value columns with Total_Products_Analyzed, Products_Need_Restock, Products_Healthy, Avg_Days_Remaining (round to 1 decimal).

Schedule a calendar event "Inventory Review Meeting" on March 12, 2026 from 9:00 AM to 10:00 AM UTC with a description listing products that need restocking. Also send an email to procurement@company.com with subject "Urgent Restock Alert" listing the products that need immediate restocking.
