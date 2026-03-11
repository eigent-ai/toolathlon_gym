# Equity Peer Comparison Guide

## Extracting Financial Data from JSONB Fields

The financial data service stores information in structured data fields. Here is how to interpret them:

### Stock Info Data
The stock information contains key-value pairs including:
- `shortName`: Company display name
- `sector`: Industry sector classification
- `marketCap`: Total market capitalization in USD
- `trailingPE`: Trailing 12-month Price-to-Earnings ratio
- `forwardPE`: Forward Price-to-Earnings ratio
- `dividendYield`: Annual dividend yield (already expressed as a percentage, e.g., 2.12 means 2.12%)
- `beta`: Stock beta relative to market (1.0 = market average)
- `fiftyTwoWeekHigh`: Highest price in the last 52 weeks
- `fiftyTwoWeekLow`: Lowest price in the last 52 weeks

Note: Some stocks may not have a dividendYield (e.g., growth stocks). Treat missing dividend yield as 0.0%.

### Calculating YTD Return
YTD (Year-to-Date) Return measures performance from the start of the current calendar year:

1. Find the first available closing price on or after January 1 of the current year
2. Get the most recent closing price
3. Calculate: YTD_Return_Pct = ((Latest_Close - First_Close_Of_Year) / First_Close_Of_Year) * 100

### Financial Statements
Financial statements are stored with different statement types:
- Income Statement: Contains Total Revenue, Net Income, etc.
- Balance Sheet: Contains Total Assets, Total Debt, etc.
- Cash Flow: Contains Free Cash Flow, Operating Cash Flow, etc.

Use the latest annual period for each company when extracting financial metrics.

### Revenue Growth Calculation
Revenue YoY Growth = ((Current_Year_Revenue - Previous_Year_Revenue) / Previous_Year_Revenue) * 100

Use the two most recent annual income statement periods for this calculation.

### Scoring Framework
Refer to the Valuation_Framework.pdf for the complete scoring methodology, weighting scheme, and rating scale. The framework ranks each company 1-5 on five dimensions and computes a weighted average score.
