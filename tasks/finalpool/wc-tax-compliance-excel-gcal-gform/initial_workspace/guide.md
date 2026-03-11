# Tax Compliance Audit Guide

## Rate Matching Methodology

Orders are matched to tax rates using the billing state field from order data. The store maintains state-specific tax rates for certain states. For all other states, a default (federal) rate applies. This default rate has an empty state field in the tax rate configuration.

If a state has multiple configured rates, sum them together to get the total applicable rate for that state.

## Discrepancy Analysis

1. For each order, compute: Expected Tax = Order Total * (Applicable Rate / 100)
2. Compute Discrepancy = Actual Tax - Expected Tax
3. Classify each order based on the thresholds in the Tax Regulations PDF
4. Round all monetary values to 2 decimal places
5. Round rates to 4 decimal places
6. Round percentages to 1 decimal place

## State-Level Reporting

Aggregate order-level results by billing state to determine:
- Total revenue and tax amounts per state
- Compliance rate (percentage of orders within the $0.50 tolerance)
- Whether the state requires a separate filing (total actual tax > $100)
