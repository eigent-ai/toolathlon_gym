I need to benchmark our support center performance against industry standards. There is an industry benchmarks API at http://localhost:30340/api/support_benchmarks.json that has average response times, resolution rates, and customer satisfaction scores for our sector.

Pull our actual support metrics from the company data warehouse covering ticket volumes by priority, average response times, and resolution statistics. Also fetch the industry benchmark data from the API endpoint.

Use the terminal to create and run a Python script called benchmark_analyzer.py in the workspace that reads support_metrics.json and industry_benchmarks.json (create both first), compares our performance against industry standards, and outputs benchmark_comparison.json.

Create an Excel file called Support_Benchmark_Report.xlsx with three sheets. The first sheet Our_Performance should have columns Priority, Ticket_Count, Avg_Response_Hours (round to 1 decimal), and Pct_of_Total (round to 1 decimal), sorted by Priority (Critical, High, Medium, Low). The second sheet Industry_Comparison should have columns Metric, Our_Value, Industry_Avg, Variance, and Status ("Above" if we beat the benchmark, "Below" otherwise). Include metrics for Avg_Response_Time, Resolution_Rate, Customer_Satisfaction, and Tickets_Per_Agent. The third sheet Action_Plan should have Priority_Area, Current_Gap, and Recommended_Action columns with at least 3 improvement areas.

Create a Word document called Benchmark_Analysis.docx with heading "Support Center Benchmark Analysis", sections for "Performance Overview", "Industry Comparison", and "Improvement Recommendations" with specific data points from the analysis.
