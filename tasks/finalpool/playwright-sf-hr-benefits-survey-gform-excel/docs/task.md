You are an HR benefits administrator at a large company. The company is evaluating whether its benefits package is competitive compared to industry peers. A market research firm has published a benefits comparison report on a website at http://localhost:30212/benefits_comparison.html showing competitor companies' benefits packages including health insurance coverage percentages, annual PTO days, and retirement matching percentages.

Read the Benefits_Review_Guide.pdf in your workspace to understand the evaluation framework and reporting requirements.

First, browse the competitor benefits comparison website and extract the benefits data for all listed competitor companies. Then query the employee database to retrieve department-level satisfaction metrics. Specifically, get the average job satisfaction score and the average work-life balance score for each department, along with the department headcount.

Create a Google Form titled "Employee Benefits Improvement Survey" with the following questions. Question 1: "Which department are you in?" as a dropdown with all seven department names as choices. Question 2: "How satisfied are you with current health insurance coverage? (1-5)" as a linear scale from 1 to 5. Question 3: "How satisfied are you with current PTO policy? (1-5)" as a linear scale from 1 to 5. Question 4: "How satisfied are you with retirement matching? (1-5)" as a linear scale from 1 to 5. Question 5: "Which benefit improvement would you prioritize?" as a multiple choice with options "Better Health Insurance", "More PTO Days", "Higher Retirement Match", and "Other". All questions should be required.

Create an Excel workbook called Benefits_Analysis.xlsx in your workspace with three sheets.

The first sheet should be called "Competitor Comparison" with columns: Company, Health_Insurance_Pct, PTO_Days, Retirement_Match_Pct. Include all competitor companies from the website plus a row for "Our Company" with values of 80 percent health insurance, 20 PTO days, and 4.0 percent retirement match. Sort all rows alphabetically by Company.

The second sheet should be called "Department Satisfaction" with columns: Department, Avg_Job_Satisfaction, Avg_Work_Life_Balance, Headcount, Satisfaction_Rating. The satisfaction data should come from the employee database. The Satisfaction_Rating column should be "High" if the average job satisfaction is 6.55 or above, and "Moderate" otherwise. Sort by Department alphabetically.

The third sheet should be called "Gap Analysis" with columns: Benefit_Category, Our_Value, Market_Average, Gap, Priority. For each of the three benefit categories (Health Insurance, PTO Days, Retirement Match), compute the market average from competitor data (rounded to 1 decimal), calculate the gap as our value minus the market average (rounded to 1 decimal), and set Priority to "High" if the gap is negative, "Medium" if the gap is zero or slightly positive (within 1.0), and "Low" if the gap is more than 1.0 above market average.

Send an email to hr_leadership@company.com with the subject "Benefits Competitiveness Analysis & Survey Launch". The body should summarize the key gaps found and mention that the employee survey has been created for additional input.

When you are finished, call claim_done.
