I need to benchmark our support team's SLA performance against industry standards. There is an SLA benchmark report from the ServiceDesk Institute at http://localhost:30303 with industry response and resolution time benchmarks by priority level. Please visit that page and extract all the benchmark data.

Then pull our actual support ticket data from the company data warehouse. I need to see how our response times compare to industry averages, broken down by ticket priority.

Use the terminal to create and run a Python script called sla_analyzer.py in the workspace that reads sla_raw_data.json (create this with the combined web + warehouse data), performs the comparison analysis, and outputs sla_results.json.

Create an Excel file called SLA_Benchmark_Report.xlsx with three sheets. The first sheet SLA_Comparison should have columns Priority, Ticket_Count, Our_Avg_Response_Hrs, Industry_Avg_Response_Hrs, Response_Gap (our minus industry, round to 2 decimals), Avg_CSAT, and Compliance_Status ("Compliant" if our response is at or below industry average, otherwise "Non-Compliant"). Sort by Priority in this order: Critical, High, Medium, Low.

The second sheet Action_Items should have columns Priority, Response_Gap, Improvement_Needed_Pct (round Response_Gap divided by Industry_Avg times 100 to 1 decimal, only for non-compliant priorities, write 0 for compliant ones), and Recommended_Action ("Urgent review needed" for gaps > 5, "Process optimization required" for gaps 1-5, "On track" for compliant).

The third sheet Summary should have two columns Metric and Value: Total_Tickets, Compliant_Priorities, Non_Compliant_Priorities, Worst_Priority (priority with largest positive gap), Best_Priority (priority with smallest or most negative gap), Overall_CSAT (weighted average of CSAT by ticket count, round to 2 decimals).

Also schedule a calendar event titled "Q1 SLA Review Meeting" for March 14, 2026 from 2:00 PM to 3:30 PM UTC with description mentioning the non-compliant priorities and key findings. Add another event "SLA Improvement Workshop" for March 21, 2026 from 10:00 AM to 12:00 PM UTC for the team to work on process improvements.
