Our investment team needs to compile the weekly market analysis report. A financial analytics dashboard is available at http://localhost:30204/dashboard.html that displays sector performance indices, weekly returns, year-to-date returns, volatility levels, and analyst consensus ratings for five market sectors: Communication Services, Consumer Cyclical, Financial Services, Healthcare, and Energy.

We also track five individual stocks that represent these sectors: GOOGL for Communication Services, AMZN for Consumer Cyclical, JPM for Financial Services, JNJ for Healthcare, and XOM for Energy. We need to cross-reference sector-level performance with individual stock data.

Please browse the market dashboard and extract all sector performance data including weekly return, sector index value, YTD return, volatility level, analyst consensus rating, and target price upside for each of the five sectors.

Then retrieve the current stock data for each of the five tickers (GOOGL, AMZN, JPM, JNJ, XOM) from the financial data service. For each stock, get the current price, sector, market capitalization, P/E ratio, and dividend yield.

Create a Google Sheet called "Weekly_Market_Analysis" with two sheets. The first sheet called "Sector Performance" should have columns Sector, Weekly_Return, Sector_Index, YTD_Return, Volatility, Consensus, and Target_Upside, with one row for each of the five sectors. The second sheet called "Stock vs Sector" should have columns Ticker, Stock_Price, Sector, Market_Cap_B (market cap in billions, rounded to 1 decimal), PE_Ratio, Dividend_Yield_Pct, Sector_Weekly_Return, and Sector_YTD_Return. Map each stock to its corresponding sector data from the dashboard.

Next, create a Word document called "Weekly_Market_Report.docx" in the workspace as an executive summary. Include a title, a market overview paragraph, a section for each sector discussing the sector index performance alongside the representative stock, and a conclusion identifying the best and worst performing sectors for the week.

Finally, send an email from analyst@investmentfirm.com to committee@investmentfirm.com with the subject "Weekly Market Analysis Report". The body should highlight the top performing sector and any sectors with negative weekly returns.

Save all output files to the workspace directory.
