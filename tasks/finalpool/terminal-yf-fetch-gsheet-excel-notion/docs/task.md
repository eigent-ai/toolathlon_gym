The investment research team needs a comprehensive market analysis that combines stock data with macroeconomic indicators. There is a PDF file called Investment_Strategy.pdf in the workspace that describes the firm's investment guidelines and risk parameters. There is also a JSON file called market_params.json that defines the analysis parameters including lookback periods and signal thresholds. Please read both files first.

Fetch economic indicator data from the dashboard at http://localhost:30180/api/indicators.json which provides current GDP growth, inflation, unemployment, consumer confidence, and PMI data in JSON format.

Pull stock information from the market data system for three tickers: AMZN, GOOGL, and JPM. For each stock, get the company name, sector classification, and the most recent closing price. Also retrieve historical price data to calculate the approximate 30-day return percentage (comparing the most recent close to the close from roughly 30 calendar days prior).

Write and run a Python script called market_analyzer.py in the workspace. The script should read from two JSON files you create: stock_data.json (containing the stock information) and economic_data.json (containing the fetched indicators). The script should compute a simple investment signal for each stock based on the following rules: if the 30-day return is positive and consumer confidence is above 95, the signal is "BUY"; if the 30-day return is negative and inflation is above 3 percent, the signal is "SELL"; otherwise the signal is "HOLD". The script should also compute a basic correlation assessment between each stock's return and the economic conditions, rated as "Positive", "Neutral", or "Negative". Output the results to market_signals.json.

Create an Excel file called Market_Analysis_Report.xlsx in the workspace with four sheets.

The first sheet should be called Stock_Overview with columns Symbol, Name, Sector, Latest_Price (rounded to 2 decimals), and Return_30d_Pct (rounded to 2 decimals). Include the three stocks sorted alphabetically by Symbol.

The second sheet should be called Economic_Indicators with columns Indicator, Value, and Trend (set to "Favorable" if the indicator suggests positive economic conditions, or "Unfavorable" otherwise; for example, GDP growth above 2 percent and unemployment below 5 percent are favorable, while inflation above 3 percent is unfavorable). Include all five indicators.

The third sheet should be called Correlation_Matrix with columns Symbol, GDP_Correlation, Inflation_Correlation, and Unemployment_Correlation. Use qualitative assessments ("Positive", "Neutral", or "Negative") based on whether the stock's sector tends to benefit from or be hurt by the indicator direction. For example, consumer cyclical stocks tend to have positive GDP correlation and negative inflation correlation.

The fourth sheet should be called Portfolio_Signals with columns Symbol, Signal (BUY, SELL, or HOLD), and Rationale (a one-sentence explanation of why that signal was generated based on the rules above).

Publish the Stock_Overview data to a cloud spreadsheet titled "Market Analysis Live Data".

Create a knowledge base database called "Investment Research Log" with one page per stock analyzed. Each page should include the stock symbol, the signal generated, and a brief summary of the analysis.
