# Flight Risk Scoring Methodology

## Definition

A **flight risk employee** is an individual who meets BOTH of the following criteria:

1. **Job Satisfaction Score <= 4** (on a scale of 1-10): Indicates below-median satisfaction with their current role, compensation, or work environment.
2. **Performance Rating >= 4** (on a scale of 1-5): Indicates above-average performance, meaning the employee is a valuable contributor.

## Rationale

Research in organizational psychology consistently shows that high-performing employees with low job satisfaction are the most likely to voluntarily leave an organization. They have the skills and track record to find alternative employment easily, and their dissatisfaction provides the motivation to do so.

## Metrics to Compute

For each department, calculate:

- **Headcount**: Total number of employees
- **Flight Risk Count**: Number of employees meeting both criteria above
- **Flight Risk Percentage**: (Flight Risk Count / Headcount) * 100
- **Average Job Satisfaction**: Mean satisfaction score across all employees in the department

## Priority Classification

Based on Flight Risk Percentage:
- **High Priority**: > 8.3%
- **Medium Priority**: 7.9% to 8.3% (inclusive)
- **Low Priority**: < 7.9%

## Data Source

Employee data is available in the HR Analytics database, employees table. Relevant fields include job satisfaction scores (1-10 scale) and performance ratings (1-5 scale).
