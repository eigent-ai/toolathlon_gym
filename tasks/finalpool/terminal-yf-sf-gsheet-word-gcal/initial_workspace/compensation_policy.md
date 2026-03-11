# Sales Compensation Policy - Q4 Bonus Structure

## Overview
The quarterly bonus for Sales department employees is calculated based on the total revenue generated in each sales region. Every employee in the Sales department is assigned to one of the five customer regions. The region's total revenue determines which bonus tier applies to all employees assigned to that region.

## Region Assignment
Sales employees are assigned to regions in round-robin fashion. Sort all Sales department employees alphabetically by name, then assign them cyclically across the five regions sorted alphabetically: Asia Pacific, Europe, Latin America, Middle East, North America.

For example, the first employee alphabetically goes to Asia Pacific, the second to Europe, the third to Latin America, the fourth to Middle East, the fifth to North America, the sixth back to Asia Pacific, and so on.

## Bonus Calculation
Each employee's bonus is computed as:

    Bonus = Employee Salary x Bonus Percentage (from tier)

The bonus percentage is determined by looking up the region's total revenue in the bonus tiers table.

## Market Adjustment
Before finalizing bonuses, the compensation committee applies a market adjustment factor based on the Dow Jones Industrial Average (^DJI) year-over-year performance:

- If DJI is up more than 10% YoY: factor = 0.9 (reduce bonuses)
- If DJI is down more than 10% YoY: factor = 1.1 (increase bonuses)
- Otherwise: factor = 1.0 (no change)

Adjusted Bonus = Current Bonus x Market Adjustment Factor

## Budget Cap
If the total adjusted bonus pool exceeds the approved budget cap, all bonuses are proportionally scaled down so the total equals the budget cap exactly.

## Validation Rules
- No individual adjusted bonus may exceed 20% of the employee's salary
- Total bonus pool must not exceed the budget cap
