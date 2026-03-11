I need to assess employee turnover risk across our organization. There is an API endpoint at http://localhost:30302/api/turnover_benchmarks.json that provides industry turnover benchmarks and risk thresholds by department from the HR Analytics Institute. Please fetch that data.

Then pull our employee data from the company data warehouse to get department-level statistics including average job satisfaction scores, salary levels, experience, and headcount.

Use the terminal to write and run a Python script called risk_scorer.py in the workspace. The script should read a combined_data.json file (which you create with both data sources merged), calculate risk scores for each department, and output risk_assessment.json. The risk scoring should compare our satisfaction levels against industry thresholds.

Create an Excel file called Turnover_Risk_Assessment.xlsx with three sheets. The first sheet Risk_Overview should have columns Department, Employee_Count, Avg_Salary, Avg_Satisfaction, Industry_Turnover_Rate, Risk_Threshold, and Risk_Level ("High" if Avg_Satisfaction is below the risk threshold, "Medium" if within 0.5 above threshold, otherwise "Low"). Sort by Department alphabetically.

The second sheet Risk_Summary should have two columns Metric and Value with rows: Total_Departments, High_Risk_Count, Medium_Risk_Count, Low_Risk_Count, Highest_Risk_Department (department with lowest satisfaction relative to threshold), Total_At_Risk_Employees (sum of employees in High and Medium risk departments).

The third sheet Detailed_Metrics should have columns Department, Avg_Experience, Avg_Performance, Satisfaction_Gap (Avg_Satisfaction minus Risk_Threshold rounded to 2 decimals), and Estimated_Turnover_Cost (Employee_Count times Avg_Salary times Industry_Turnover_Rate divided by 100, rounded to nearest integer).

Also create a knowledge base page in Notion titled "Turnover Risk Dashboard" with a summary of findings including key metrics and recommended actions for high-risk departments.
