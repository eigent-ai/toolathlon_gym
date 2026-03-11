You are a portfolio analyst at a fund. Your workspace contains Portfolio.xlsx with the current stock holdings (symbol, company, quantity) and Investment_Policy.pdf describing the fund's investment policy.

Your task is to produce a complete portfolio analysis report. Follow these steps exactly.

Step 1: Get current stock information and 30-day price history for all five stocks in the portfolio: GOOGL, AMZN, JPM, JNJ, and XOM. Use the yahoo-finance tools to fetch current stock info and historical prices.

Step 2: Calculate the following metrics for each stock using the quantity from Portfolio.xlsx and the current price from Yahoo Finance. Current Value equals price multiplied by quantity. The 30-day return percentage equals the percentage change from the closing price 30 days ago to today's closing price. Identify the Market Cap category as Large Cap for all five stocks since they all have market caps above 100 billion dollars.

Step 3: Create a file called Portfolio_Analysis.xlsx in your workspace with two sheets. The first sheet must be named Holdings and contain one row per stock with these columns: Symbol, Company, Sector, Quantity, Current_Price, Current_Value, Return_30d_Pct. The second sheet must be named Summary and contain a metric-value table with these rows: Total_Portfolio_Value (sum of all current values), Best_Performer (symbol with highest 30-day return), Worst_Performer (symbol with lowest 30-day return), and one row per sector listing that sector name and the total value of holdings in that sector.

Step 4: Write a Word document called Investment_Memo.docx in your workspace. The document must have the title heading "Portfolio Analysis Report". Then include a section heading "Holdings Overview" followed by a table showing all five stocks with their symbol, company, sector, quantity, current price, current value, and 30-day return. Then include a section heading "Performance Analysis" describing which stock was the best performer, which was the worst, and the overall portfolio value. Then include a section heading "Recommendations" with at least two sentences of investment commentary based on the data.

Step 5: Send an email from analyst@fund.example.com to investment-committee@fund.example.com with the subject "Monthly Portfolio Analysis Report". The body should include the total portfolio value and a brief summary of the best and worst performers.

Complete all five steps and call claim_done when finished.
