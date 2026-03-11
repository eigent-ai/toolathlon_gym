I want to create a market overview for a set of stocks I follow. The tickers I track are AMZN, GOOGL, JNJ, JPM, and XOM. For each of these, I need the company name, the sector it belongs to, the most recent closing price, and then the returns over two time horizons.

For the 30-day return, take the closing price from 30 trading days ago and compute the percentage change to the latest price. Do the same for the 90-day return using the price from 90 trading days ago. A trading day means an actual day where the market was open and there is price data, so count backwards through the available daily price records rather than using calendar days.

Create an Excel file called Market_Overview.xlsx in the workspace with a single sheet named "Stock Summary". The columns should be Symbol, Company_Name, Sector, Latest_Price, Price_30d_Ago, Return_30d_Pct (rounded to 2 decimal places), Price_90d_Ago, Return_90d_Pct (rounded to 2 decimal places). Sort the rows alphabetically by Symbol.

Then create a page in my notes system titled "Market Dashboard". Add a paragraph block to the page that summarizes which stock had the best 30-day return and which had the worst 30-day return, including the ticker symbol and the return percentage for each.
