I need a comprehensive analysis of our support ticket resolution performance. Please query the support ticket system in our data warehouse to pull ticket data and break it down by issue type and by priority level.

For the issue type breakdown, I want to see each issue type alongside the total number of tickets, the count of resolved tickets (those with status "Closed"), the average resolution time in hours (calculated from the difference between resolved and created timestamps, only for tickets that have a resolved timestamp) rounded to 1 decimal place, and the average customer satisfaction score rounded to 2 decimal places.

For the priority breakdown, I need each priority level with the total ticket count, the average response time in hours rounded to 1 decimal place, and the SLA compliance percentage rounded to 1 decimal place, where a ticket is SLA-compliant if its response time in hours is less than or equal to its SLA hours.

Please create a Google Sheet titled "Support Resolution Analysis" with two sheets. The first sheet should be called "By Issue Type" with columns Issue_Type, Total_Tickets, Resolved_Count, Avg_Resolution_Hours, and Avg_Satisfaction, sorted by Avg_Resolution_Hours from highest to lowest. The second sheet should be called "By Priority" with columns Priority, Ticket_Count, Avg_Response_Hours, and SLA_Compliance_Pct, sorted alphabetically by Priority.

After creating the spreadsheet, send an email to support-lead@company.com with the subject "Support Resolution Performance Report" mentioning which issue type has the longest average resolution time and the overall SLA compliance situation across priorities.
