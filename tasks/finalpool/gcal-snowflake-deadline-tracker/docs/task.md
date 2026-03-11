Our support operations team needs a comprehensive SLA compliance audit for response times on our high-priority and medium-priority tickets. All the ticket data lives in our company data warehouse, along with the SLA policy definitions that specify the maximum allowed response time for each priority level.

Please query the data warehouse to find all tickets with High or Medium priority. For each ticket, compare its actual response time against the response target defined in the SLA policies table. A ticket is considered "Breached" if its response time exceeds the SLA response target, "Near Breach" if the response time is above 80 percent of the target but at or below the target, and "Compliant" otherwise.

Create an Excel file called SLA_Compliance_Audit.xlsx in the workspace with two sheets:

Sheet 1 named "Breached Tickets" should list every High and Medium priority ticket that breached its response SLA target. Include the following columns in this order: Ticket_ID, Priority, Issue_Type, Created_At (formatted as YYYY-MM-DD HH:MM), Response_Time_Hours (the actual response time rounded to 2 decimal places), SLA_Target_Hours (the response target from the SLA policy), Hours_Over_SLA (response time minus target, rounded to 2 decimal places), Customer_Satisfaction (the CSAT score). Sort all rows first by Priority (High before Medium), then by Hours_Over_SLA in descending order.

Sheet 2 named "Summary" should have these columns: Priority, Total_Tickets, Breached_Count, Near_Breach_Count, Compliant_Count, Breach_Rate_Pct (breached count divided by total times 100, rounded to 1 decimal place), Avg_Response_Hours (rounded to 2 decimal places), Avg_CSAT (average customer satisfaction rounded to 2 decimal places). Include one row for High priority and one row for Medium priority, in that order.

Next, create follow-up review calendar events for the top 5 worst SLA breaches (the 5 tickets with the highest Hours_Over_SLA regardless of priority). Each event should be scheduled on 2026-03-07 from 09:00 to 09:30, with the title "SLA Review: [Ticket_ID]" and the description should state "Response SLA breach review for [Ticket_ID]. Priority: [Priority]. Response time: [Response_Time_Hours]h vs target: [SLA_Target_Hours]h. [Hours_Over_SLA]h over SLA."

Create a page in the team knowledge base titled "SLA Breach Dashboard - March 2026" that summarizes the audit findings. Include the overall breach counts by priority, the top issue types contributing to breaches, and the average customer satisfaction for breached tickets.

Finally, send an alert email to support-lead@company.com with the subject "SLA Compliance Alert - Response Time Breaches" from sla-monitor@company.com. The email body should highlight the total number of High priority breaches, the total number of Medium priority breaches, the breach rates for each priority level, and list the 5 worst-offending ticket IDs.
