The VP of Sales has asked me to prepare a Q2 2026 sales forecast presentation for the upcoming board meeting. A market research firm has published their industry growth projections for 2026, and the data is available as a JSON API at http://localhost:30209/api/projections.json. This API provides expected growth rates by region for the electronics and consumer products sector.

Please start by fetching the market growth projections from that API. The data includes projected growth percentages for each of our five sales regions.

Next, query the sales data warehouse for our Q1 2026 historical performance. I need the total revenue and order count broken down by region for January, February, and March. Also get the total Q1 revenue by customer segment for each region to understand our segment mix.

Using the Q1 actuals as a baseline and applying the market growth projections, calculate the Q2 2026 forecast for each region. The Q2 forecast revenue for each region should be calculated as Q1 total revenue multiplied by (1 + growth_rate/100), where growth_rate comes from the market projections API. Round all monetary values to two decimal places.

Create an Excel file called Sales_Forecast_Data.xlsx in the workspace with three sheets. The first sheet should be called "Q1_Actuals" with columns Region, Month, Order_Count, and Revenue showing the monthly breakdown. The second sheet should be called "Q2_Forecast" with columns Region, Q1_Revenue, Growth_Rate_Pct, Q2_Forecast_Revenue, and Q2_Forecast_Orders. The third sheet should be called "Segment_Mix" with columns Region, Segment, Q1_Revenue, and Revenue_Share_Pct showing each segment's share of total regional revenue as a percentage.

Then create a PowerPoint presentation called Q2_Sales_Forecast.pptx in the workspace. The presentation should have a title slide with "Q2 2026 Sales Forecast" as the title and today's date. Add a slide summarizing Q1 performance by region with total revenues. Add a slide showing the growth projections from the market research. Add a slide with the Q2 forecast by region. Add a final slide with key takeaways and the region with the highest projected growth.

Finally, schedule a board presentation in the calendar on March 28, 2026 from 10:00 to 11:30 with the title "Board Meeting: Q2 Sales Forecast Presentation". In the description, include the total company-wide Q2 forecast revenue and the top-performing region by projected growth.
