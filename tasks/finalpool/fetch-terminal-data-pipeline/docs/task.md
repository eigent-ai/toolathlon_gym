The data engineering team recently received raw API response dumps from two internal systems. The files sales_api_response.json and inventory_api_response.json are already in your workspace. The sales file contains order records with fields like order_id, product_id, product_name, quantity, unit_price, and order_date. The inventory file contains product stock records with product_id, product_name, current_stock, reorder_point, and warehouse. Both files may have duplicate entries and inconsistent capitalization in product names.

Your workspace also has an empty memory file at memory/memory.json for tracking progress.

Complete the following steps.

First, read both JSON files to understand their structure and contents.

Second, write a Python script called clean_data.py that performs the following cleaning operations. For the sales data, remove duplicate entries based on order_id, keeping the first occurrence of each. For the inventory data, remove duplicate entries based on product_id, keeping the first occurrence. Normalize all product_name values to title case in both datasets. For each unique product in the sales data, calculate the total revenue as quantity multiplied by unit_price across all orders for that product. The script should output two files: cleaned_sales.json containing the deduplicated sales records, and cleaned_inventory.json containing the deduplicated inventory records. Run the script after writing it.

Third, store a note in your memory summarizing what you have done so far, including the number of unique sales records and inventory records after cleaning.

Fourth, create an Excel file called Data_Pipeline_Report.xlsx in your workspace with three sheets.

The first sheet should be called "Sales Analysis" with columns Product_Name, Total_Quantity_Sold, Total_Revenue, and Avg_Unit_Price. There should be one row per product showing the total quantity sold across all orders, the total revenue (sum of quantity times unit_price for each order), and the average unit price. Only include products that appear in the cleaned sales data.

The second sheet should be called "Inventory Status" with columns Product_Name, Current_Stock, Reorder_Point, and Status. Status should be "LOW" if the current stock is less than or equal to the reorder point, and "OK" otherwise. Include all products from the cleaned inventory data.

The third sheet should be called "Combined View" with columns Product_Name, Total_Sold, Current_Stock, Revenue, and Stock_Status. This sheet merges data from the sales analysis and inventory status. Total_Sold is the total quantity sold for that product. Current_Stock and Stock_Status come from the inventory data. Revenue is the total revenue for that product. Include all products that appear in either dataset.

Fifth, create a Google Sheet titled "Pipeline Dashboard" containing the same data as the Combined View sheet from the Excel file.
