I need to create a portfolio monitoring system. Start by pulling current stock information and historical prices for our tracked stocks (GOOGL, AMZN, JPM, JNJ, XOM). Get their latest prices, sectors, and recent price history.

Read the Investment_Policy.pdf in the workspace which outlines our target allocation percentages and risk tolerance parameters.

Use the terminal to create and run a Python script called portfolio_monitor.py in the workspace that reads stock_data.json and policy_data.json (create both first), calculates current portfolio allocation assuming equal initial investment of $10,000 per stock, determines drift from target allocation, and outputs portfolio_status.json.

Create a Google Sheet titled "Portfolio Monitor Dashboard" with three sheets. The first sheet Holdings should have columns Symbol, Company, Sector, Current_Price (round to 2 decimals), Shares_Held (round to 2 decimals), Market_Value (round to 2 decimals), and Allocation_Pct (round to 1 decimal), sorted by Symbol. The second sheet Performance should have columns Symbol, Purchase_Price (round to 2 decimals), Current_Price (round to 2 decimals), Return_Pct (round to 2 decimals), and Status ("Gain" or "Loss"). The third sheet Rebalancing should have columns Symbol, Current_Allocation (round to 1 decimal), Target_Allocation (round to 1 decimal), Drift_Pct (round to 1 decimal), and Action ("Buy", "Sell", or "Hold" based on drift direction and magnitude).

Schedule a calendar event "Portfolio Rebalancing Review" on March 17, 2026 from 2:00 PM to 3:00 PM UTC with description listing stocks that need rebalancing.

Send an email to investment-team@company.com with subject "Portfolio Drift Alert" listing any stocks with allocation drift exceeding 3 percentage points.
