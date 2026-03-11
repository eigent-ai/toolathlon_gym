You are an investment assistant helping an investor track upcoming dividend payments for their stock portfolio.

The investor holds positions in several stocks and wants to identify which ones pay dividends, then organize dividend information for easy tracking.

First, look up stock information for the following tickers: GOOGL, AMZN, JPM, JNJ, XOM. For each stock, check whether it pays a dividend by looking at the dividend rate. Only include stocks that have a dividend rate greater than zero.

For each dividend-paying stock, collect the following information: ticker symbol, company name (short name), dividend rate, dividend yield (as a percentage), ex-dividend date, and payout ratio.

Create an Excel file called "Dividend_Tracker.xlsx" in your workspace with two sheets:

The first sheet should be named "Dividend Stocks" and contain columns: Ticker, Company, Dividend_Rate, Dividend_Yield, Ex_Dividend_Date, Payout_Ratio. Include one row per dividend-paying stock, sorted by ticker symbol alphabetically.

The second sheet should be named "Summary" with the following rows of information: Total_Dividend_Stocks (count of stocks with dividends), Avg_Yield (average dividend yield across dividend stocks), Highest_Yield_Ticker (the ticker with the highest dividend yield).

Next, create a Google Calendar event for each dividend-paying stock to remind the investor of the ex-dividend date. Each event should have the summary "Ex-Dividend: [TICKER]" (replacing [TICKER] with the actual ticker symbol), and the description should mention the dividend rate. Schedule each event as an all-day event on the ex-dividend date.

Finally, create a Google Sheet titled "Dividend Watch List" with a sheet named "Overview" that contains the same columns and data as the "Dividend Stocks" sheet in the Excel file.
