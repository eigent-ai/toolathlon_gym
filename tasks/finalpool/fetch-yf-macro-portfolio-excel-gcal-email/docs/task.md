You are a portfolio manager at a mid-sized investment firm. Your firm tracks five core holdings: GOOGL, AMZN, JPM, JNJ, and XOM. A research service has published its latest macroeconomic indicator forecasts, which you need to incorporate into your portfolio analysis. Read the Investment_Strategy.pdf file in your workspace first to understand the firm's approach to macro-sensitive portfolio management.

The research service API is available at http://localhost:30211/api/macro_forecast.json and provides GDP growth, inflation rate, and interest rate forecasts by quarter for 2026. Fetch this data to understand the macro outlook.

After retrieving the macro forecast, query the financial data source for current stock information on all five holdings, including their current price, sector, market capitalization, P/E ratio, and beta values.

Create an Excel workbook called Macro_Portfolio_Analysis.xlsx in your workspace with three sheets.

The first sheet should be called "Macro Forecast" and contain columns: Quarter, GDP_Growth_Pct, Inflation_Rate_Pct, Interest_Rate_Pct. Populate it with the four quarters of data from the research API (Q1 2026 through Q4 2026).

The second sheet should be called "Stock Holdings" and contain columns: Symbol, Sector, Price, Market_Cap_B (market cap in billions rounded to 1 decimal), PE_Ratio (rounded to 1 decimal), Beta. List all five stocks sorted alphabetically by Symbol.

The third sheet should be called "Sector Sensitivity" and contain columns: Sector, Avg_GDP_Growth, Rate_Sensitivity, Recommended_Action. For each unique sector among the five holdings, compute the average annual GDP growth from the macro forecast (average of the 4 quarters, rounded to 1 decimal), assign a Rate_Sensitivity label based on the sector's beta values (High if average beta for that sector is above 1.0, Low otherwise), and set Recommended_Action to "Overweight" if Rate_Sensitivity is High and average GDP growth is above 2.0 percent, "Underweight" if Rate_Sensitivity is Low and average GDP growth is below 2.0 percent, and "Hold" for all other cases. Sort by Sector alphabetically.

Schedule a Google Calendar event called "Q2 Portfolio Rebalancing Review" on March 30, 2026 from 14:00 to 15:30. In the description, list the five holdings and note the average GDP growth forecast and the overall recommended portfolio stance based on the majority of sector recommendations.

Send an email to investment_committee@firm.com with the subject "Macro Outlook & Portfolio Impact - Q2 2026". The body should summarize the macro forecast highlights (average GDP growth, inflation trend, interest rate direction) and list any sectors recommended for Overweight or Underweight adjustment.

When you are finished, call claim_done.
