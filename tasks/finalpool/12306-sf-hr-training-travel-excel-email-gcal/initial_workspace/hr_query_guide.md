This guide explains how to query the HR data warehouse to identify training candidates and plan their travel.

Employee Selection Criteria:
Query the HR_ANALYTICS.PUBLIC.EMPLOYEES table in the data warehouse.
Filter for employees where DEPARTMENT is in Sales or Marketing.
Filter for employees where YEARS_EXPERIENCE is 3 or greater.
Limit the results to 5 employees maximum.
Note each employee ID, name, department, years of experience, and salary for the report.

Training Eligibility:
All employees meeting the department and experience criteria are eligible for this training.
Mark each selected employee as Training_Eligible = Yes in the report.

Travel Planning:
The training requires employees to travel from Beijing to Shanghai on the training date.
Select a high-speed train departing Beijing South early enough to arrive in Shanghai before the training kickoff at 15:00.
Employees should plan to return to Beijing on the same day after the training concludes.
Use second-class seats (二等座) as the standard booking class.

Report Structure:
The travel report should contain three sections:
1. An employee list with their HR data
2. A detailed travel plan listing each employee and their specific train for each direction
3. A budget summary showing outbound ticket costs, return ticket costs, and the grand total

Budget Calculation:
Multiply the number of employees by the ticket price for each direction to get the subtotal.
The grand total is the sum of outbound and return subtotals.
Second-class seat price between Beijing and Shanghai is 553 CNY per ticket.
