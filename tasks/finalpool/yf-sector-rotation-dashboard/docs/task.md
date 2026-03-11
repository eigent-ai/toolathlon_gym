I am an investment analyst and I need you to help me build a sector rotation performance dashboard as an Excel report. I want to compare five stocks representing different sectors over the past year: AMZN for Consumer Cyclical, GOOGL for Communication Services, JNJ for Healthcare, JPM for Financial Services, and XOM for Energy.

First, use Yahoo Finance to look up each stock's closing price on 2025-03-06 (one year ago) and 2026-03-05 (the most recent trading day), then calculate the one-year percentage return for each stock. Also pull the latest quarterly income statement for each stock from Yahoo Finance to get the most recent quarterly revenue and net income figures.

Next, visit the internal research portal at http://localhost:30145 to get the sector benchmark target returns and analyst consensus ratings for each stock. The portal has a page with all of this information.

Finally, compile everything into an Excel file called sector_rotation_report.xlsx saved in the workspace. The file should have three sheets.

The first sheet should be named "Performance" with these columns in order: Symbol, Sector, Price_1Y_Ago, Current_Price, Return_Pct, Benchmark_Return_Pct, Alpha, Analyst_Rating, Target_Price, Upside_Pct. Return_Pct is the one-year return as a percentage rounded to two decimal places. Alpha is Return_Pct minus Benchmark_Return_Pct rounded to two decimal places. Upside_Pct is the percentage difference between the analyst target price and the current price, rounded to two decimal places. The rows should be ordered as AMZN, GOOGL, JNJ, JPM, XOM.

The second sheet should be named "Financials" with these columns: Symbol, Revenue_Latest_Q, Net_Income_Latest_Q, Profit_Margin_Pct. Revenue and net income should be expressed in millions (divide the raw number by one million) and rounded to two decimal places. Profit margin is net income divided by revenue times 100, rounded to two decimal places. Same row order: AMZN, GOOGL, JNJ, JPM, XOM.

The third sheet should be named "Summary" and should use a simple key-value layout where column A has the label and column B has the value. The rows should be: Best_Performer (the symbol with the highest Return_Pct), Worst_Performer (the symbol with the lowest Return_Pct), Avg_Alpha (the average Alpha across all five stocks rounded to two decimal places), Stocks_Above_Benchmark (the count of stocks where Alpha is greater than zero), Stocks_Below_Benchmark (the count of stocks where Alpha is less than zero).
