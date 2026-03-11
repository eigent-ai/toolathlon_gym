The product team wants to analyze customer review quality across product categories to prioritize product improvement efforts. Query WooCommerce product review data and link it to product categories to understand how different categories perform with customers.

Create an Excel file called Product_Review_Analysis.xlsx with two sheets. The first sheet should be called "Category Analysis" with columns: Category, Product_Count, Review_Count, Avg_Rating (rounded to 2 decimal places), Five_Star_Count, and Five_Star_Rate (the percentage of reviews that are 5 stars, rounded to 1 decimal). Sort by Category alphabetically. The second sheet should be called "Top Products" and list the top 10 highest-rated products that have at least 3 reviews, with columns: Product_Name (truncated to 50 characters if needed), Category, Review_Count, and Avg_Rating (rounded to 2 decimal places). Sort by Avg_Rating descending, then Review_Count descending.

Create a Notion database called "Product Review Insights" with properties for Category (title), Product_Count (number), Review_Count (number), Avg_Rating (number), and Five_Star_Rate (number). Populate it with one entry per category from the Category Analysis sheet.

Email the analysis to product_team@store.com with subject "Product Review Analysis Report" and include a summary of which categories have the highest and lowest ratings in the email body.
