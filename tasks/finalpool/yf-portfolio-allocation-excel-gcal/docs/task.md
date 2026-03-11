You are a portfolio manager creating an asset allocation plan for a new investment portfolio. There is a PDF file called Portfolio_Guidelines.pdf in your workspace that contains the investment strategy guidelines approved by the investment committee. Read that document first to understand the allocation constraints and strategy.

Then connect to the Yahoo Finance data source and retrieve current stock information for all available tracked stocks, including their current price, analyst recommendation, and sector.

Create an Excel file called Portfolio_Allocation.xlsx in your workspace with two sheets. The first sheet should be called "Stock Analysis" with columns: Symbol, Price, Sector, Recommendation, Allocated_Weight_Pct. Following the guidelines in the PDF which favor strong_buy rated stocks, assign allocation weights as follows: GOOGL gets 25.0 percent, AMZN gets 25.0 percent, JPM gets 20.0 percent, JNJ gets 15.0 percent, and XOM gets 15.0 percent. Sort the rows alphabetically by Symbol.

The second sheet should be called "Allocation Summary" with columns: Metric, Value. Include the following rows: Total_Invested with a value of 100000, Strong_Buy_Count with the count of stocks rated strong_buy, Buy_Count with the count of stocks rated buy, and Weighted_Avg_Price computed as the sum of each stock's price multiplied by its weight percentage divided by 100, rounded to 2 decimal places.

Schedule a Google Calendar event called "Portfolio Rebalancing" on April 30, 2026 from 10:00 to 11:30. Include a description mentioning the five tracked stocks and the total portfolio value of $100,000.

Send an email to portfolio_manager@wealth.com with subject "Portfolio Allocation Plan - April 2026" summarizing the allocation strategy and the key metrics from the Allocation Summary sheet.

When you are finished, call claim_done.
