You are a financial analyst tasked with investigating whether there is a correlation between public stock market performance and the company's internal sales performance. Your goal is to compare stock price trends for key market indicators with the company's sales data from the data warehouse, then present findings to the CFO.

Start by reading the Analysis_Framework.pdf in your workspace which outlines the correlation methodology and presentation requirements.

Retrieve current stock information for the following five tickers: AMZN, GOOGL, JNJ, JPM, and XOM. For each stock, get the current price, the 52-week high, the 52-week low, the market capitalization, and the year-to-date percentage change. Also get the current price of gold (ticker GC=F) and the Dow Jones Industrial Average (ticker ^DJI) as market benchmarks.

Query the data warehouse to get monthly revenue data. Use the SALES_DW analytics monthly revenue table to retrieve month, total revenue, and order count for the most recent 12 months available. Also query the sales orders table to get a breakdown of total revenue and order counts by customer segment (Enterprise, SMB, Consumer, etc.) by joining with the customers table.

Write and run a Python script called correlation_analysis.py in your workspace. The script should compute a simple comparison table showing each stock's YTD performance alongside the company's revenue trend direction (increasing or decreasing compared to the prior month). The script should also calculate the total company revenue across all segments and the segment with the highest revenue contribution.

Create a PowerPoint presentation called Market_Correlation_Report.pptx in your workspace with at least six slides.

Slide 1 should be a title slide with "Market and Sales Correlation Analysis" as the title and today's date as the subtitle.

Slide 2 should present the stock market overview with a table showing each of the five stocks plus gold and Dow Jones, with columns for Ticker, Current Price, 52-Week High, 52-Week Low, and Market Cap where applicable.

Slide 3 should present the company's monthly revenue trend, showing the last several months of revenue data in a table with columns Month, Revenue, and Order Count.

Slide 4 should show the customer segment breakdown with columns Segment, Revenue, Order Count, and Revenue Share percentage.

Slide 5 should present the correlation findings, listing each stock alongside its YTD performance and noting whether the company's revenue trend appears to move in the same or opposite direction.

Slide 6 should be a summary slide with key takeaways and three recommendations for the CFO about investment strategy alignment with sales performance.

Send an email to cfo@company.com with the subject "Market and Sales Correlation Analysis Report". The email body should summarize the key findings including the total company revenue, the top performing stock by YTD change, the largest customer segment by revenue, and a note that the detailed PowerPoint presentation has been prepared for review.
