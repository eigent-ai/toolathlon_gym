I need to build a Q2 2026 sales forecast by combining our historical sales data with external market projections. There is a market intelligence API at http://localhost:30304/api/market_projections.json that provides regional growth rates and market size data. Please fetch that data.

Then pull our current sales data from the company data warehouse, broken down by region, including order counts and total revenue.

Use the terminal to create and run a Python script called forecast_builder.py in the workspace that reads both data sources from JSON files (create historical_sales.json and market_outlook.json), applies the growth rates to calculate forecasted revenue, and outputs sales_forecast.json.

Create an Excel file called Sales_Forecast_Q2_2026.xlsx with three sheets. The first sheet Regional_Forecast should have columns Region, Current_Orders, Current_Revenue, Growth_Rate_Pct, Forecasted_Revenue (Current_Revenue times 1 plus Growth_Rate divided by 100, round to 2 decimals), and Revenue_Increase (Forecasted minus Current, round to 2 decimals). Sort by Region alphabetically.

The second sheet Forecast_Summary should have two columns Metric and Value: Total_Current_Revenue, Total_Forecasted_Revenue, Total_Revenue_Increase, Avg_Growth_Rate (simple average of all regional growth rates, round to 1 decimal), Highest_Growth_Region, Lowest_Growth_Region, Total_Orders.

The third sheet Growth_Ranking should rank regions by growth rate descending with columns Rank, Region, Growth_Rate_Pct, Current_Revenue, and Market_Share_Pct (region current revenue divided by total current revenue times 100, round to 1 decimal).

Also create a Word document called Q2_Forecast_Report.docx with heading "Q2 2026 Sales Forecast Report" and sections for Market Overview (describe the market conditions), Regional Analysis (discuss each region's growth prospects), and Strategic Recommendations (at least 3 recommendations). Each section should reference specific numbers from the analysis.

Finally send an email to sales-team@company.com with subject "Q2 2026 Sales Forecast Ready" summarizing the total forecasted revenue and highest growth region.
