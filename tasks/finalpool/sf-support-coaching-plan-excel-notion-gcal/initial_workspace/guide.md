# Agent Performance Coaching Methodology

## Calculating SLA Compliance

SLA compliance measures how often an agent responds to tickets within the response target defined in the SLA policies table. The response target varies by ticket priority:

- Critical: 1 hour
- High: 4 hours
- Medium: 8 hours
- Low: 24 hours

To calculate SLA compliance for each agent:
1. Join the tickets table with the SLA policies table on the priority field.
2. For each ticket, check if RESPONSE_TIME_HOURS is less than or equal to RESPONSE_TARGET_HOURS from the SLA policies.
3. SLA Compliance = (number of compliant tickets / total tickets) * 100, rounded to 1 decimal place.

## Calculating CSAT

Average CSAT is the arithmetic mean of the CUSTOMER_SATISFACTION field (scale 1-5) across all tickets handled by the agent, rounded to 2 decimal places.

## Identifying Agents

The reporter field in the tickets table identifies which agent handled the ticket. Each unique reporter value represents one agent.

## Assigning Performance Tiers

Use the tier definitions from the Coaching Framework PDF. Both SLA compliance and CSAT thresholds must be met for an agent to qualify for a tier. Evaluate tiers from highest (Elite) to lowest (Needs Improvement) and assign the first tier where both criteria are satisfied.

## Focus Area Assignment

Apply the focus area rules from the framework in the listed priority order. The first rule that matches determines the primary focus area. The second matching rule determines the secondary focus area. If fewer than two rules match, assign Leadership Development to fill remaining slots.

For the high ticket volume check, compare the agent's ticket count against the average ticket count across all agents.
For the below-average CSAT check, compare against the mean CSAT across all agents.
