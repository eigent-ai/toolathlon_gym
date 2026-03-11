I need to benchmark our company's salaries against the latest industry data. There is a 2026 salary benchmark report from CompAnalytics Research available at http://localhost:30301 that I need you to check. Please visit that page and pull all the benchmark salary figures by department.

Then access our internal HR data warehouse to get our actual average salaries per department, along with employee count, average years of experience, and average performance rating.

Before building the final report, use the terminal to write and run a Python script called salary_processor.py in the workspace that reads a JSON file called benchmark_raw.json (create this with the web data), cross-references it with a file called internal_salaries.json (create this with the warehouse data), and outputs a file called salary_comparison.json with the merged analysis.

Create an Excel file called Salary_Benchmark_Report.xlsx with three sheets. The first sheet Compensation_Comparison should have columns Department, Employee_Count, Our_Avg_Salary, Industry_Benchmark, Difference (Our minus Industry, round to 2 decimals), Difference_Pct (round Difference divided by Industry_Benchmark times 100 to 1 decimal), and Status (write "Above" if Difference >= 0 otherwise "Below"). Sort alphabetically by Department.

The second sheet Department_Details should have columns Department, Avg_Experience, Avg_Performance, Our_Avg_Salary, and a Salary_Per_Year_Exp column calculated as Our_Avg_Salary divided by Avg_Experience rounded to 2 decimals. Sort alphabetically.

The third sheet Executive_Summary should have two columns Metric and Value with rows: Total_Departments, Departments_Above_Benchmark, Departments_Below_Benchmark, Highest_Gap_Department (department with largest positive Difference), Lowest_Gap_Department (department with most negative Difference), Average_Difference (mean of all Difference values rounded to 2 decimals), Overall_Status ("Competitive" if more departments above than below, otherwise "Needs Attention").

Also send an email to hr-director@company.com with subject "2026 Salary Benchmark Analysis Complete" and a body summarizing the key findings: how many departments are above vs below benchmark, which department has the biggest gap, and the overall status.
