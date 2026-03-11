You are an HR compensation analyst tasked with conducting a comprehensive salary benchmarking study. You need to compare internal salary data against external market benchmarks, schedule review meetings, and communicate findings to the HR team.

Start by reading the Compensation_Policy.pdf in your workspace which outlines the company's compensation philosophy and the review criteria for salary adjustments.

Fetch the external salary benchmark data from http://localhost:30405/api/benchmarks.json. This JSON file contains industry salary benchmarks organized by department, including median salary, 25th percentile, 75th percentile, and the market trend (growing, stable, or declining) for each department.

Query the data warehouse to retrieve the internal salary statistics for each department. For each of the seven departments (Engineering, Finance, HR, Operations, R&D, Sales, Support), calculate the employee count, average salary rounded to two decimal places, minimum salary, maximum salary, average years of experience, and average job satisfaction score.

Write and run a Python script called compensation_analysis.py in your workspace. The script should compare each department's average internal salary against the external benchmark median. Calculate the gap as a percentage: (internal_avg minus benchmark_median) divided by benchmark_median times 100. Flag departments where the gap exceeds plus or minus 10 percent as needing review. The script should also identify departments where average job satisfaction is below 6.5, which might indicate compensation-related dissatisfaction.

Schedule salary review meetings on the shared calendar for the week of March 16 to March 20, 2026. Create one meeting for each of the seven departments. Each meeting should be titled with the department name followed by "Salary Review Meeting". Schedule them as 1-hour meetings, two per day starting at 10 AM and 2 PM, with the last department on Friday morning. Include in the event description the department's average salary and its gap percentage compared to the benchmark.

Create an Excel workbook called Compensation_Benchmark_Report.xlsx in your workspace with three sheets.

The first sheet should be named Department_Analysis and contain columns Department, Employee_Count, Avg_Salary, Min_Salary, Max_Salary, Avg_Experience, and Avg_Satisfaction. Include one row for each of the seven departments.

The second sheet should be named Salary_Benchmark and contain columns Department, Internal_Avg, Benchmark_Median, Benchmark_25th, Benchmark_75th, Gap_Pct, Market_Trend, and Needs_Review. Include one row for each department. The Needs_Review column should show Yes if the gap exceeds plus or minus 10 percent, otherwise No.

The third sheet should be named Review_Summary and contain columns Department, Review_Date, Review_Time, Key_Issue, and Recommended_Action. Include one row for each department with the scheduled meeting date and time, the primary issue identified (salary gap or satisfaction concern), and a recommended action (increase, maintain, or restructure).

Send an email to hr_team@company.com with the subject "Compensation Benchmarking Study Complete". The email body should summarize the overall findings: how many departments need salary review, which department has the largest gap from the benchmark, the average gap across all departments, and a note that review meetings have been scheduled for the week of March 16. Also mention that the detailed Excel report is available.
