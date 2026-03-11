I need to optimize our product pricing based on competitor intelligence. There is a competitor pricing dashboard at http://localhost:30305 with current competitor prices for products in our categories. Please visit that page and extract all the pricing data.

Then pull our current product catalog from the online store to get our product names, prices, stock quantities, and sales figures.

Use the terminal to create and run a Python script called price_optimizer.py in the workspace. The script should read competitor_prices.json and our_products.json (both of which you create), match products by name, calculate price differences, and output price_recommendations.json with optimization suggestions.

Create an Excel file called Price_Optimization_Report.xlsx with three sheets. The first sheet Price_Comparison should have columns Product_Name, Our_Price, Competitor_Price, Price_Difference (our minus competitor, round to 2 decimals), Difference_Pct (round Price_Difference divided by Competitor_Price times 100 to 1 decimal), and Recommendation ("Reduce price" if we are more than 15 percent above competitor, "Maintain" if within 15 percent, "Consider increase" if below competitor). Sort by Product_Name alphabetically.

The second sheet Category_Summary should summarize by product category from the store with columns Category, Product_Count, Avg_Our_Price (round to 2 decimals), and Avg_Stock.

The third sheet Executive_Summary should have Metric and Value columns with Total_Products_Compared, Products_Overpriced (more than 15 percent above), Products_Competitive (within 15 percent), Products_Underpriced (below competitor), Avg_Price_Gap (average of all Difference_Pct, round to 1 decimal).

Also create a Word document called Pricing_Strategy.docx with heading "Pricing Strategy Recommendations" and sections for Market Position Analysis, Product-Level Recommendations, and Implementation Timeline with at least 2 sentences each.
