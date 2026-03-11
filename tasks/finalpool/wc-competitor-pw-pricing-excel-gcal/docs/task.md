I need a competitive pricing analysis for our online store. There is a competitor price comparison dashboard at http://localhost:30341 that shows pricing data for products similar to ours. Please visit that page and extract the competitor pricing information.

Then pull our current product catalog from the online store with prices, stock levels, and sales data.

Use the terminal to create and run a Python script called pricing_analyzer.py in the workspace that reads competitor_prices.json and our_products.json (create both first), compares pricing, calculates price positioning metrics (percentage above or below competitor average), identifies opportunities for price adjustments, and outputs pricing_analysis.json.

Create an Excel file called Competitive_Pricing_Analysis.xlsx with three sheets. The first sheet Price_Comparison should have columns Product_Name, Our_Price (round to 2 decimals), Competitor_Avg (round to 2 decimals), Price_Diff (round to 2 decimals), Price_Position_Pct (round to 1 decimal, positive means above competitor), and Recommendation ("Reduce" if more than 15% above, "Maintain" if within 15%, "Increase" if more than 15% below), sorted by Product_Name. The second sheet Market_Position should have Metric and Value columns with Products_Above_Market, Products_Below_Market, Products_At_Market, Avg_Price_Gap_Pct (round to 1 decimal), and Revenue_At_Risk (round to 2 decimals). The third sheet Action_Items should have Product, Current_Price, Suggested_Price (round to 2 decimals), Expected_Impact, and Priority columns for products needing price changes.

Schedule a calendar event "Pricing Strategy Review" on March 14, 2026 from 10:00 AM to 11:30 AM UTC with description listing the top 3 products with the largest price gaps.
