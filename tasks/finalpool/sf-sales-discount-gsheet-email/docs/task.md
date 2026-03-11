I want to understand how discounts affect our sales performance across different customer segments. Please look at all delivered orders in our sales data warehouse and join them with customer information to group everything by customer segment.

For each segment, I need the total order count, how many of those orders had a discount applied (where the discount value is greater than zero), the average discount percentage among discounted orders rounded to 2 decimal places, total revenue rounded to 2 decimals, and revenue from discounted orders only rounded to 2 decimals.

Create a Google Sheet called "Discount Analysis Report" with a sheet named "Segment Analysis". The columns should be Segment, Order_Count, Discounted_Orders, Discount_Rate_Pct (which is the percentage of orders that had discounts, rounded to 1 decimal), Avg_Discount_Pct, Total_Revenue, Discounted_Revenue, and Revenue_Impact_Pct (the percentage of total revenue that comes from discounted orders, rounded to 1 decimal). Sort the rows by Discount_Rate_Pct from highest to lowest.

After that, send an email to finance-team@company.com with the subject "Segment Discount Analysis" summarizing which customer segment uses discounts the most frequently and what the overall discount rate is across all segments.
