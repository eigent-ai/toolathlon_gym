As the Learning and Development manager, I need to conduct a training needs assessment by cross-referencing employee performance data with our available training programs. The goal is to identify underperforming employees and match them with appropriate courses while staying within our budget constraints.

Start by reading the Training Policy PDF in your workspace. It outlines the total annual budget, maximum spend per employee, and the priority rules for selecting which employees receive training. Pay close attention to the performance rating threshold that determines eligibility.

Next, fetch the training course catalog from our internal API at http://localhost:30214/api/training_catalog.json. This returns a JSON array of available courses, each with a course ID, title, target department, level, duration in hours, and cost. Some courses are department-specific while others are tagged for all departments.

Also read the department heads JSON file in your workspace, which maps each department name to the department head email address.

Now query our HR employee database. We have an employees table with fields including employee name, department, role, performance rating on a 1 to 5 scale, years of experience, education level, and salary. Identify all employees whose performance rating is the lowest possible score (rating equals 1), as these are the highest priority for training according to the policy.

Create an Excel workbook called Training_Needs.xlsx with three sheets. The first sheet should be named "Low Performers" with columns for Employee_Name, Department, Role, Performance_Rating, Years_Experience, and Education_Level. Include all employees with the lowest performance rating, sorted by department alphabetically and then by employee name within each department.

The second sheet should be named "Recommended Courses" and should show, for each department, which course is recommended. Include columns Department, Course_Title, Course_Cost, Employee_Count (number of low performers in that department), and Total_Cost (course cost times employee count). For each department, if a department-specific course exists, choose the least expensive one. If no department-specific course exists, assign the least expensive general course (those marked for all departments). Sort by department alphabetically.

The third sheet should be named "Budget Summary" with columns Metric and Value. Include the following rows: Total_Eligible_Employees (total count of employees with the lowest rating), Total_Departments (number of departments with at least one eligible employee), Estimated_Total_Cost (sum of all Total_Cost values from the Recommended Courses sheet), Available_Budget (use five hundred thousand as the annual training budget), Budget_Remaining (Available_Budget minus Estimated_Total_Cost), and Within_Budget which should be "Yes" if the estimated total cost is within the available budget or "No" otherwise.

Finally, send an email to each department head listed in the department heads file. Each email should have a subject line in the format "Training Plan for [Department]" and the body should mention the number of low-performing employees in their department, the recommended course title, the per-employee cost, and the total cost for their department. Send these emails from training-manager@company.com.
