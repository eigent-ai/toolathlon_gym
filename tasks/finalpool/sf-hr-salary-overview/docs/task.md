I need a comprehensive salary analysis report for our HR department. There is a PDF file called Salary_Benchmarks.pdf in the workspace that contains the annual salary benchmarks approved by leadership for each department. Please read that first.

Then connect to our company data warehouse and pull the current employee salary data. I need a breakdown by department showing how many employees are in each, what the average, minimum, and maximum salaries are, and how those compare to the benchmarks.

Create an Excel file called HR_Salary_Report.xlsx in the workspace with two sheets. The first sheet should be called "Department Analysis" with columns Department, Employee_Count, Avg_Salary rounded to 2 decimal places, Min_Salary, Max_Salary, Benchmark from the PDF, Variance which is Avg_Salary minus Benchmark rounded to 2 decimals, and Variance_Pct which is Variance divided by Benchmark times 100 rounded to 1 decimal place. Sort alphabetically by Department.

The second sheet should be called "Summary" with two columns Metric and Value. Include Total_Employees across all departments, Overall_Avg_Salary as the weighted average across all employees rounded to 2 decimals, Overall_Benchmark as the simple average of all department benchmarks, Departments_Above_Benchmark counting how many departments have positive Variance, and Departments_Below_Benchmark for the rest.
