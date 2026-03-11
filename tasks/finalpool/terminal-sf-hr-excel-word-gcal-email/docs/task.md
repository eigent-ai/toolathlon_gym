You are an HR analytics specialist responsible for preparing the annual performance review cycle for the organization. Your goal is to analyze performance rating distributions across all departments, generate review worksheets, draft a policy memo, schedule department review meetings, and notify department managers.

Start by reading the Performance_Review_Policy.pdf in your workspace, which describes the rating scale definitions and calibration rules. Also review the review_schedule.json file that contains preferred meeting times and department manager contacts.

Query the company data warehouse to retrieve employee performance data. The relevant data is in the HR Analytics database, specifically the employees table. For each department, calculate the headcount, average performance rating, the percentage of employees with a rating of 4 or above (high performers), and the percentage of employees with a rating below 2 (underperformers). The seven departments are Engineering, Finance, HR, Operations, R&D, Sales, and Support.

Write a Python script called rating_analysis.py in your workspace and execute it using command-line tools. The script should calculate the median performance rating for each department and compute the overall rating distribution across the entire organization by grouping ratings into five buckets: rating 1, rating 2, rating 3, rating 4, and rating 5. It should also calculate the 25th and 75th percentile of ratings for each department.

Create an Excel workbook called Performance_Review_Report.xlsx in your workspace with four sheets.

The first sheet should be named Department_Ratings and contain columns for department, headcount, avg_rating, median_rating, pct_above_4, and pct_below_2. Include one row per department with the computed statistics. Round avg_rating to two decimal places and percentages to one decimal place.

The second sheet should be named Rating_Distribution and contain columns for rating_value, count, and pct. Include five rows, one for each integer rating from 1 to 5, showing the total number of employees at that rating and the percentage of the total workforce.

The third sheet should be named Review_Calendar and contain columns for department, review_date, and time. Schedule one review meeting per department across the week of March 9 to March 13, 2026. Assign one department per day starting Monday. Meetings should be at 2:00 PM.

The fourth sheet should be named Policy_Summary and contain columns for metric and value. Include rows summarizing key organizational metrics: total_employees, overall_avg_rating, highest_rated_department, lowest_rated_department, total_high_performers (rating 4 or above), and total_underperformers (rating below 2).

Create a Word document called Review_Policy_Memo.docx in your workspace. The document should contain a title "Annual Performance Review Policy Memo", an overview section explaining the purpose and scope of the review cycle covering all seven departments, a section on rating distribution findings highlighting the overall average rating and the proportion of high performers and underperformers, and a section on recommended calibration actions for departments where the percentage of high performers exceeds 36 percent or the percentage of underperformers exceeds 6 percent.

Schedule the seven department review meetings on the shared calendar for the week of March 9 to March 13, 2026. Since there are seven departments and five weekdays, schedule two meetings on Friday (one at 2 PM and one at 4 PM). Each event should have a summary like "Performance Review - [Department Name]" and last one hour.

Send an email to hr_leadership@company.com with the subject "Annual Performance Review Cycle - Department Summary" containing a brief summary of the overall average rating, the department with the highest average rating, and the total number of employees flagged as underperformers.
