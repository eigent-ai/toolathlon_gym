I need to reconcile our internal KPI targets against actual performance data. There is an executive KPI dashboard at http://localhost:30342/api/kpi_targets.json that has our quarterly targets for revenue, ticket resolution, employee satisfaction, and other key metrics.

Pull actual performance data from the company data warehouse covering sales revenue, support ticket metrics, and HR satisfaction scores.

Use the terminal to create and run a Python script called kpi_reconciler.py in the workspace that reads kpi_targets.json and actual_metrics.json (create both first), compares targets vs actuals, calculates achievement rates, and outputs kpi_reconciliation.json.

Create an Excel file called KPI_Dashboard_Report.xlsx with four sheets. The first sheet KPI_Scorecard should have columns KPI_Name, Target, Actual (round to 2 decimals), Achievement_Pct (round to 1 decimal), and Status ("Met" if achievement >= 100%, "Near" if >= 90%, "Missed" otherwise), sorted by Achievement_Pct ascending. The second sheet Revenue_Detail should have columns Region, Target_Revenue (round to 2 decimals), Actual_Revenue (round to 2 decimals), and Variance_Pct (round to 1 decimal), sorted by Region. The third sheet Support_Detail should have columns Priority, Target_Response_Hours, Actual_Avg_Hours (round to 1 decimal), and Met_SLA ("Yes" or "No"). The fourth sheet Executive_Summary should have Metric and Value columns with KPIs_Met, KPIs_Near, KPIs_Missed, Overall_Achievement_Pct (round to 1 decimal), and Top_Risk_Area.

Create a Word document called KPI_Review.docx with heading "Quarterly KPI Performance Review", sections for "Executive Summary", "Revenue Performance", "Support Center KPIs", and "Action Items for Missed Targets".

Send an email to executive-team@company.com with subject "Q1 KPI Performance Summary" highlighting the overall achievement rate and listing any missed KPIs with their shortfall percentages.
