You are an HR analytics specialist tasked with measuring the effectiveness of internal training programs. The company uses a learning management system to deliver training courses to employees, and you need to cross-reference course completion data with employee performance metrics from the company data warehouse.

Start by reading the training_catalog.json file in your workspace. It maps internal training courses to company departments and describes expected outcomes. Also review roi_framework.md which explains how to calculate training ROI, and department_benchmarks.csv which contains baseline performance metrics for each department before the training programs began.

Query the learning management system for courses 9 and 10, which are both titled "Data-Driven Design" but offered in different terms. Retrieve enrollment data and submission scores for all assignments in both courses. Course 9 maps to the Engineering department and course 10 maps to the R&D department according to the training catalog.

Query the company data warehouse for employees in the Engineering and R&D departments. Retrieve their employee IDs, names, performance ratings, job satisfaction scores, education levels, and years of experience.

Write a Python script called training_matches.py in your workspace that matches employees to course completions. The matching logic should work by comparing employee counts and department mappings from the training catalog. For each department, compute the number of enrolled students, the number of submissions, and the overall average assignment score. Save the results as training_matches.json in the workspace.

Execute the script using command-line tools. Then write a second Python script called effectiveness_analysis.py that reads training_matches.json and the department benchmark data to compute training effectiveness metrics. For each department calculate the average assignment score from the course data, the average employee performance rating from the data warehouse, the completion rate (ratio of students with submissions to total enrolled students), and the performance gap (difference between the current average performance rating and the baseline from department_benchmarks.csv, where Engineering baseline is 3.00 and R&D baseline is 2.95). Execute this script and save the output as effectiveness_analysis.json in the workspace.

Create an online survey form titled "Training Feedback Survey" with exactly 5 questions. The first question should be "Overall Training Satisfaction" as a rating from 1 to 5. The second question should ask "Which module was most useful?" as a free text response. The third question should ask "What improvements would you suggest?" as a free text response. The fourth question should ask "Would you recommend this training to colleagues?" with radio choices "Yes" and "No". The fifth question should ask "Preferred training format" with radio choices "Online", "In-Person", and "Hybrid".

Write a third Python script called survey_analysis.py in your workspace that reads the survey responses from the form and combines them with the effectiveness analysis. The script should compute the average satisfaction rating from survey responses, count how many respondents would recommend the training, and determine the most common preferred format. Save the combined analysis as survey_results.json.

Execute the script. Then create a Word document called Training_Effectiveness_Report.docx in the workspace. The document should have the following sections.

The first section should be titled "Executive Summary" and provide an overview stating that this report analyzes the effectiveness of Data-Driven Design training programs delivered to Engineering and R&D departments.

The second section should be titled "Methodology" and explain that the analysis cross-references course completion data from the learning management system with employee performance metrics from the HR data warehouse, supplemented by participant feedback surveys.

The third section should be titled "Performance Impact Analysis" and contain a subsection for each department. For Engineering, report the average assignment score from course 9, the number of enrolled students, the average employee performance rating, and the performance improvement over the 3.00 baseline. For R&D, report the same metrics using course 10 data and the 2.95 baseline.

The fourth section should be titled "Survey Findings" and summarize the average satisfaction rating, the recommendation rate as a percentage, and the most preferred training format based on the survey responses.

The fifth section should be titled "ROI Estimation" and state that based on the performance improvements observed and the training completion rates, the estimated return on investment is calculated as (average performance improvement across departments divided by 0.25) times 100, expressed as a percentage.

The sixth section should be titled "Recommendations" and include a conditional recommendation. If the average performance improvement across both departments is less than 0.15 rating points, recommend restructuring the training program with more hands-on components. If the improvement is 0.15 or more, recommend expanding the program to additional departments such as Sales and Finance.

Send an email from training_analytics@company.com to hr_director@company.com with the subject "Training Effectiveness Analysis - Key Findings". The email body should include the overall average assignment score across both courses, the average performance rating for the two departments combined, the performance improvement over baseline for each department, and a note about the survey satisfaction rating.

Send a second email from training_analytics@company.com to training_team@company.com with the subject "Training Feedback Survey Results". The email body should include the average satisfaction score, the number of respondents who would recommend the training, the most preferred training format, and a summary of common improvement suggestions from the survey responses.
