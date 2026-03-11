I need a product ranking report from our SALES_DW data warehouse. Please query the orders and products data, focusing only on orders that have been delivered, and rank the products by total revenue within each product category.

Create an Excel file called "Product_Rankings.xlsx" in the workspace. The first sheet should be named "Rankings" with these columns: Category, Product_Name, Brand, Units_Sold, Revenue (rounded to 2 decimal places), and Rank_In_Category. Only include the top 5 products per category, ranked by revenue descending. Sort the rows by Category alphabetically and then by Rank_In_Category ascending.

Add a second sheet called "Category Totals" with columns: Category, Total_Products_Sold (sum of all units sold in that category, not just top 5), Total_Revenue (rounded to 2 decimal places, sum of all revenue in that category, not just top 5), and Top_Product (the name of the highest-revenue product in that category). Sort the rows by Total_Revenue in descending order.

Finally, create a Google Sheet titled "Product Rankings Dashboard" and populate it with the same data as the Rankings sheet from the Excel file.
