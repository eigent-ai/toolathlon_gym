You are a support operations analyst. Analyze the support center performance using the support tickets database.

Calculate SLA compliance and customer satisfaction metrics per ticket priority. For SLA compliance, use these response time thresholds: High priority tickets must be responded to within 4 hours, Medium within 8 hours, and Low within 24 hours.

For each priority level compute the total ticket count, the number of SLA-compliant tickets, the compliance rate as a percentage rounded to 2 decimal places, and the average customer satisfaction score rounded to 2 decimal places.

Create a Google Sheet titled Support Center Performance Dashboard with two sheets:

Sheet named SLA_Compliance with columns: Priority, Total_Tickets, SLA_Compliant, Compliance_Rate, Avg_CSAT. Include one row per priority (High, Medium, Low).

Sheet named Summary with two columns: Metric and Value. Include: Best_Priority (priority with highest average CSAT score) and Worst_SLA_Priority (priority with lowest SLA compliance rate).

Create a Google Forms survey titled Customer Support Satisfaction Survey with exactly 4 questions. The first question asks whether the issue was resolved satisfactorily with Yes, No, and Partially as options. The second asks how the customer would rate the response speed with numeric options from 1 to 5. The third asks how they would rate the support agent with numeric options from 1 to 5. The fourth asks whether they would contact the support team again with Yes and No as options.

Send an email from analytics@company.example.com to support-management@company.example.com with subject Support Center Performance Report - SLA Compliance Analysis. The body should summarize key findings including SLA compliance rates and CSAT scores.

The SLA_Policy_Reference.pdf file in your workspace contains the SLA policy documentation for reference.
