You are a support operations manager. Analyze individual support agent performance from the support center ticket database.

Query the tickets table to calculate per-agent metrics using the reporter column as the agent identifier. For each unique reporter, compute the total tickets handled, the average response time in hours rounded to 2 decimal places, the average customer satisfaction score rounded to 2 decimal places, and the SLA compliance rate as a percentage rounded to 2 decimal places. For SLA compliance, a ticket is compliant when the response time falls within the threshold for its priority level: High priority tickets must be responded to within 4 hours, Medium within 8 hours, and Low within 24 hours.

Also query the agents table to retrieve the team and skill level for any agents listed there. The five reporters in the tickets data are: Alice, Bob, Charlie, Emily, and John.

Create a Google Sheet titled Agent Performance Scorecard with two sheets:

Sheet named Scorecards with columns: Agent_Name, Total_Tickets, Avg_Response_Hrs, Avg_CSAT, SLA_Compliance_Rate. Include one row per agent (5 agents total, sorted by Total_Tickets descending).

Sheet named Rankings with columns: Rank_Type, Rank, Agent_Name, Value. Include the top 3 agents by Avg_CSAT (Rank_Type = Top_CSAT) and the top 3 agents by Total_Tickets (Rank_Type = Top_Volume).

Schedule a Google Calendar event titled Agent Performance Review exactly 10 days after the launch time. The event should last 1 hour.

Send an email from support-manager@company.example.com to performance-review@company.example.com with subject Agent Performance Review - Monthly Scorecard. The body should summarize the top performing agent by CSAT and the highest volume agent.

The Agent_Evaluation_Rubric.pdf file in your workspace contains the evaluation criteria for reference.
