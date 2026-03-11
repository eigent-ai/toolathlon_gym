You are a portfolio analyst preparing for the upcoming earnings season. Your workspace contains two files you should read first. The file earnings_playbook.md describes the firm's strategy for managing positions around earnings announcements, including pre-earnings position sizing rules. The file alert_template.txt provides the standard email template for earnings alerts sent to the investment team.

Begin by visiting the earnings calendar portal at http://localhost:30225/index.html which displays the upcoming earnings dates and analyst expectations for three of the firm's holdings: GOOGL, AMZN, and JPM. The page shows each stock's expected earnings date, the consensus expected earnings per share, and the expected quarterly revenue in billions. Read all data from that page carefully.

Next connect to the stock data source and retrieve the historical financial statement data for GOOGL, AMZN, and JPM. For each stock, look up the quarterly income statement data to find the most recent four quarters of diluted EPS values. This will allow you to compute each stock's historical average EPS and identify whether the upcoming expectations deviate from the historical trend.

Also retrieve the current stock price and sector information for each of the three stocks, plus JNJ and XOM which are also portfolio holdings but do not have upcoming earnings in the calendar.

Create an Excel workbook called Earnings_Analysis.xlsx in your workspace with three sheets. The first sheet should be named "Earnings Calendar" with columns Symbol, Name, Earnings_Date, Expected_EPS, Historical_Avg_EPS, and Surprise_Trend. The Historical_Avg_EPS should be the simple average of the most recent four quarters of diluted EPS from the financial statement data, rounded to two decimal places. The Surprise_Trend should be "Above" if the expected EPS exceeds the historical average, "Below" if it is less, or "In Line" if they are within 5 percent of each other. Populate this with the three stocks that have upcoming earnings (GOOGL, AMZN, JPM), sorted alphabetically by symbol.

The second sheet should be named "Financial Trends" with columns Symbol, Period, Diluted_EPS, and Total_Revenue. Include rows for the most recent four quarters of each of the three earnings stocks (12 rows total), sorted by symbol then by period descending.

The third sheet should be named "Alert Summary" with columns Metric and Value. Include: Stocks_Reporting with the count of stocks that have upcoming earnings (3), Earliest_Report with the earliest earnings date among the three, Latest_Report with the latest earnings date, Avg_Expected_EPS with the simple average of the three expected EPS values rounded to two decimal places, and Stocks_Above_Historical counting how many have expected EPS above their historical average.

Finally, send an email to investment-team@company.com with the subject "Earnings Season Alert - Q1 2026" summarizing which stocks are reporting soon, their expected dates, and highlighting any stocks where the expected EPS deviates significantly from historical averages.

When you are finished, call claim_done.
