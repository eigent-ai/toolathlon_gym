I need to put together a peer comparison report for our equity research coverage. We track five individual stocks and I need a thorough analysis comparing them across multiple dimensions.

Start by reading the Valuation_Framework.pdf in your workspace, it has the complete methodology we use for scoring and rating companies. There is also a guide.md file with helpful details on how to extract and calculate the various metrics.

Connect to the financial data service and pull stock information for all available individual stocks, skip any indices or commodity futures, we only want the actual company equities. For each company get the current stock info including market cap, P/E ratio, dividend yield, beta, and 52-week price range.

Then pull the price history so you can calculate the year-to-date return for each stock. Also retrieve the latest annual financial statements, we need revenue, net income, total assets, and free cash flow from the income statement, balance sheet, and cash flow statement respectively. For the revenue growth calculation grab the previous year revenue too.

Now apply the scoring framework from the PDF. Rank each company 1 to 5 on the five dimensions, valuation, growth, income, risk, and momentum, then compute the weighted score and overall rating using the weights specified in the framework document.

Create an Excel file called Peer_Comparison.xlsx in your workspace with three sheets. First sheet "Company Profiles" should have columns Symbol, Company_Name, Sector, Market_Cap, Trailing_PE, Dividend_Yield_Pct, Beta, Fifty_Two_Week_High, Fifty_Two_Week_Low, Latest_Close, YTD_Return_Pct. Sort by Symbol alphabetically and round market cap to 0 decimals, everything else to 2 decimals. Second sheet "Financial Comparison" with columns Symbol, Revenue, Net_Income, Total_Assets, Free_Cash_Flow, all rounded to 0 and sorted by Symbol. Third sheet "Scoring" with Symbol, Valuation_Rank, Growth_Rank, Income_Rank, Risk_Rank, Momentum_Rank, Weighted_Score rounded to 2, and Overall_Rating as text.

Build an investor presentation called Investor_Presentation.pptx with at least 6 slides covering a title slide, market overview listing the companies and sectors, company profiles summary with key metrics, financial comparison highlighting revenue and profitability, scoring results showing the rankings and weighted scores, and investment recommendations summarizing the buy hold sell calls.

Finally send three emails. First email to portfolio_managers@firm.com with subject "Peer Comparison Summary" giving an overall summary of the analysis results, which stocks are rated Buy and which are Hold, and the key takeaways. Second email to research_team@firm.com with subject "Peer Comparison Detailed Findings" including the detailed scoring breakdown for each company and the financial metrics. Third email to compliance@firm.com with subject "Peer Comparison Risk Review" highlighting any companies with elevated risk characteristics like high beta or negative YTD returns and noting any potential concerns with the recommendations.

When everything is done call claim_done.
