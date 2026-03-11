You are a research analyst preparing a cross-sector stock comparison report. Your workspace contains Investment_Universe.md describing the five stocks and their sectors, and Analysis_Criteria.txt listing the financial metrics to compare.

Your task is to compare five stocks from different sectors on key financial metrics. Follow these steps exactly.

Step 1: Retrieve current stock information for GOOGL, AMZN, JPM, JNJ, and XOM using the yahoo-finance tools. Gather the current price, market capitalization, trailing P/E ratio, 52-week high, and 52-week low for each stock.

Step 2: Create an Excel file called Sector_Comparison.xlsx in your workspace with two sheets. The first sheet must be named Metrics and contain exactly five rows (one per stock) with these columns: Symbol, Company, Sector, Market_Cap_B (market cap in billions rounded to two decimal places), Current_Price, PE_Ratio (trailing P/E rounded to two decimal places, or N/A if not available), High_52w, Low_52w. The second sheet must be named Sector_Summary and contain exactly five rows with these columns: Sector, Symbol, Market_Cap_B, Price_Assessment (the value "Above_Avg" if the stock's current price is above the average price of all five stocks, or "Below_Avg" otherwise).

Step 3: Create a Google Forms survey titled "Investment Preference Survey" with exactly four questions. The first question must be "Which sector do you prefer for long-term investment?" with multiple choice options: Communication Services, Consumer Cyclical, Financial Services, Healthcare, Energy. The second question must be "What is your investment horizon?" with multiple choice options: Short-term (less than 1 year), Medium-term (1 to 3 years), Long-term (more than 3 years). The third question must be "What is your risk tolerance?" with multiple choice options: Low, Medium, High. The fourth question must be "Which financial metric matters most to you?" with multiple choice options: Dividend Yield, P/E Ratio, Revenue Growth Rate, Market Capitalization.

Step 4: Send an email from research@fund.example.com to investors@fund.example.com. The subject must contain "Sector Comparison". The body should summarize the key findings including the stock with the largest market cap, the highest P/E ratio, and the 52-week range highlights for at least two stocks.

Complete all four steps and call claim_done when finished.
