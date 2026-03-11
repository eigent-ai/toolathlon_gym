You are a strategic pricing analyst tasked with evaluating how commodity and market price movements may affect e-commerce product margins. Your goal is to analyze financial market trends for gold futures and a major consumer cyclical stock, compare them with the online store's product pricing and sales performance, and produce strategic recommendations.

Start by reading the Pricing_Strategy.pdf in your workspace, which describes the margin targets and pricing principles used by the company. Also review the analysis_params.json file that contains the parameters for the correlation analysis and margin calculations.

Query the financial data service to retrieve historical price data for two symbols: gold futures (GC=F) and Amazon stock (AMZN). For each symbol, obtain the average closing price over the available history, the percentage price change from the earliest to the most recent data point, and a volatility measure using the standard deviation of closing prices.

Query the e-commerce platform to retrieve all products with their names, categories, regular prices, and total sales. Group the products by category and calculate the average price, estimated cost (at 60 percent of price), estimated margin percentage, and total sales volume for each category.

Write a Python script called correlation_analysis.py in your workspace and execute it using command-line tools. The script should compute a simple analysis comparing the financial indicators with product category performance. For the correlation analysis, note that gold prices represent commodity cost pressure (higher gold suggests inflation and higher input costs), while AMZN stock performance represents consumer spending confidence. The script should output a summary of whether the current market conditions suggest expanding or contracting product margins.

Create an Excel workbook called Commodity_Impact_Analysis.xlsx in your workspace with four sheets.

The first sheet should be named Stock_Trends and contain columns for symbol, name, avg_price, price_change_pct, and volatility. Include one row for GC=F (Gold Futures) and one row for AMZN (Amazon). The avg_price should be the mean of all historical closing prices, price_change_pct should measure the change from earliest to latest close as a percentage, and volatility should be the standard deviation of closing prices.

The second sheet should be named Product_Margins and contain columns for category, avg_price, avg_cost_estimate, margin_pct, and total_sales. The avg_cost_estimate is 60 percent of the average price. The margin_pct is 40 percent (since cost is 60 percent of price). Include one row per product category.

The third sheet should be named Correlation_Analysis and contain columns for factor_pair, correlation_description, and implication. Include at least two rows: one analyzing the relationship between gold price trends and product cost pressure, and another analyzing consumer spending confidence based on AMZN stock performance versus product sales volumes.

The fourth sheet should be named Strategic_Recommendations and contain columns for category, current_margin, target_margin, and action. For each product category, the current margin is 40 percent. If gold prices have risen significantly (over 50 percent change) suggesting cost inflation, recommend a target margin of 35 percent with action "Monitor costs and consider price adjustment". Otherwise recommend maintaining 40 percent with action "Maintain current pricing".

Create a Word document called Pricing_Strategy_Memo.docx in your workspace. The document should have a title "Commodity Impact and Pricing Strategy Memo", a market overview section summarizing gold and AMZN price trends with specific numbers, a product margin analysis section summarizing the category-level margins and sales performance, and a strategic recommendations section advising whether to adjust pricing based on the market conditions observed.

Set up a database in the team wiki system called "Market Research Dashboard" with properties for Analysis Topic (title), Market Indicator (rich text), Current Value (number), and Trend (select with options Up, Down, Stable). Add two entries: one for Gold Futures summarizing the gold price trend and one for Consumer Confidence summarizing the AMZN stock trend.
