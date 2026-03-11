You are an inventory planner for an online retail store. You need to forecast when products will run low on stock and schedule reorder dates with suppliers, accounting for their lead times.

Start by reading the reorder policy document in your workspace. It describes the safety stock level, review horizon, and the step-by-step calculation for determining which products need reordering and when. There is also a sales velocity spreadsheet template that you will fill with data from the store.

Retrieve all published products from your online store that currently have stock greater than zero. Note each product's ID, name, category, current stock quantity, and regular price. Also retrieve all completed and processing orders to calculate sales velocity. For each product, determine the total number of units sold across all completed and processing orders by examining the order line items.

Calculate the number of days covered by your order history by finding the difference between the earliest and latest order dates for completed and processing orders. Then compute the average daily sales for each product by dividing total units sold by the number of days in that period.

Fetch the supplier lead times from the API endpoint at http://localhost:30202/api/lead_times.json which provides lead times in days for each product category.

Apply the reorder policy calculations. For each product, compute the effective stock as the current stock minus the safety stock of 5 units with a minimum of zero. Calculate the days until safety stock is reached by dividing effective stock by average daily sales. If a product's days until safety stock is 90 days or fewer and the product has any sales history, it needs reordering. The reorder date is calculated as today plus the days until safety stock minus the supplier lead time for that category. If the calculated reorder date falls on or before today, schedule it for tomorrow instead.

Create an Excel file called Inventory_Forecast.xlsx in your workspace with two sheets. The first sheet named "Stock Analysis" should have columns Product_ID, Product_Name, Category, Current_Stock, Avg_Daily_Sales, Days_Until_Safety_Stock, Lead_Time, Needs_Reorder, and Reorder_Date. Include all products with stock greater than zero. Mark Needs_Reorder as Yes or No, and set Reorder_Date to the calculated date or N/A for products that do not need reordering. The second sheet named "Reorder Schedule" should list only the products needing reorder with columns Product_Name, Category, Current_Stock, Reorder_Date, and Lead_Time_Days.

For each product that needs reordering, create a Google Calendar event on the calculated reorder date from 09:00 to 10:00. Set the event summary to "Reorder: " followed by the product name, and include the current stock level and lead time in the event description.

When you have completed all tasks, call claim_done.
