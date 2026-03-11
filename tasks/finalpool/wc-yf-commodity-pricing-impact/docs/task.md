You are a supply chain analyst for an online electronics and accessories retailer. Your company sells products across several categories including watches, electronics, cameras, audio equipment, home appliances, and TV systems. Recently, gold and other commodity prices have been volatile, and leadership wants to understand how these commodity price movements might affect product costs and margins across different product categories.

Start by fetching the commodity price indices from the company's internal supply chain portal at http://localhost:30236/api/commodity_indices.json to get the latest reference data on gold, silver, copper, electronics materials, and rare earth price indices.

Next, retrieve the historical gold futures price data from the financial data service for the ticker symbol GC=F. You will need the closing prices for the most recent 30 trading days to calculate a 30 day moving average and determine the overall price trend direction (whether prices are generally rising or falling over this period).

Then connect to the store's product catalog and retrieve all products, paying attention to their categories and prices. Group the products by their category and calculate the average price and total product count for each category.

Review the supply chain notes file in your workspace which describes the approximate material cost composition for each product category. Using these percentages, estimate the material cost component of the average product price for each category. Also review the margin targets document which specifies target profit margins by category.

For the gold price trend analysis, create a sheet called "Gold Price Trend" in an Excel file named Commodity_Impact.xlsx with columns for Date, Gold_Close, Moving_Avg_30d, and Trend_Direction. The trend direction for each row should indicate "Up" if the closing price is above the 30 day moving average, and "Down" if it is below. Include the 30 most recent trading days.

Create a second sheet called "Category Analysis" in the same Excel file. This sheet should have columns for Category, Avg_Price, Product_Count, Estimated_Material_Cost_Pct (the material cost percentage from the notes), Estimated_Material_Cost (the dollar amount based on average price times the material cost percentage), Target_Margin_Pct (from the margin targets document), and Current_Margin_vs_Target (whether the implied margin meets or falls short of the target). Include all seven product categories.

Create a third sheet called "Correlation Summary" that provides a high level summary row with the current gold price, the 30 day moving average, the overall trend (Up or Down based on whether the latest price is above the 30 day MA), the number of categories analyzed, and which categories are most sensitive to commodity price changes (those with the highest material cost percentages).

Finally, create a Word document called Commodity_Report.docx that provides a narrative analysis of the findings. The report should discuss the current gold price trend, summarize product category exposure to commodity price movements, highlight which categories face the greatest margin pressure from rising material costs, and provide recommendations for pricing strategy adjustments.

When you have completed all tasks, call claim_done.
