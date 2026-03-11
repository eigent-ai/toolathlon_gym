The People Analytics team wants to assess workforce diversity across all departments, focusing on educational background distribution as a key diversity metric. There is a PDF file called Diversity_Policy.pdf in the workspace that outlines the company's diversity goals and target thresholds. There is also a JSON file called analysis_parameters.json that defines the diversity index threshold (a Shannon entropy score of 1.2 or above is considered meeting the target). Please read both files first to understand the policy context and analysis parameters.

Connect to the company data warehouse and query the employee table to get the count of employees grouped by department and education level. There are seven departments and five education levels, resulting in thirty-five unique combinations.

Write and run a Python script called diversity_calculator.py in the workspace that computes the Shannon diversity index for each department based on its education level distribution. The Shannon diversity index is calculated as the negative sum of p times the natural log of p for each education level proportion p within a department, where p is the fraction of employees at that education level out of the department total. The script should read from a file called dept_education_data.json (which you create from the queried data) and output diversity_results.json containing the index for each department.

Create an Excel file called Diversity_Metrics_Report.xlsx in the workspace with four sheets.

The first sheet should be called Department_Breakdown with columns Department, Education_Level, Employee_Count, Pct_of_Department (the percentage of that education level within the department rounded to one decimal place), and Diversity_Index (the Shannon entropy for that department rounded to four decimal places, repeated for each row of the same department). Sort by Department alphabetically, then by Education_Level alphabetically.

The second sheet should be called Education_Analysis with columns Education_Level, Total_Count, and Pct_of_Total (percentage of the entire workforce rounded to one decimal place). Sort by Total_Count descending.

The third sheet should be called Survey_Config with columns Question_Number (1 through 5), Question_Text, and Question_Type. The five survey questions should cover department affiliation, current education level, perceived barriers to further education, interest in company-sponsored education programs, and suggestions for improving workforce diversity. Use appropriate question types such as multiple choice, checkbox, or free text.

The fourth sheet should be called Summary with columns Metric and Value. Include the following metrics: Total_Employees (the total headcount), Num_Departments (the number of departments), Avg_Diversity_Index (the average Shannon index across all departments rounded to four decimal places), Departments_Meeting_Target (the count of departments with a diversity index at or above 1.2), and Highest_Diversity_Department (the department name with the highest Shannon index).

After creating the Excel file, create an online survey form called "Workforce Diversity Assessment Survey" with five questions matching the survey configuration defined in the Excel file.

Finally, create a database in the team wiki called "Diversity Metrics Dashboard" with one page per department. Each page should represent a department and include the department name, headcount, diversity index, and whether it meets the target threshold.
