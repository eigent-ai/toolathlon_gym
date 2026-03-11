## Benchmark Review Guide

### Data Sources
- **External Benchmarks**: Industry Analytics Dashboard (internal portal) - access via web browser
- **Internal Metrics**: Company data warehouse (Snowflake)

### Cross-Reference Methodology
1. Extract benchmark values from the dashboard for each metric
2. Query internal data warehouse for corresponding internal values
3. Calculate gaps: Internal Value - Industry Average
4. Calculate gap percentage: (Internal - Industry) / Industry * 100
5. Classify gaps per the rules in Benchmark_Context.pdf
6. Assign priorities based on classification

### Metrics Mapping
| Dashboard Metric | Internal Calculation |
|---|---|
| Avg Salary | AVG of all employee salaries |
| Employee Satisfaction | AVG of job satisfaction scores |
| Revenue Per Employee | Total order revenue / Total employees |
| Avg Order Value | AVG of order total amounts |
| Customer Retention Rate | N/A - not directly calculable |
| SLA Compliance Rate | N/A - not directly calculable |

### Notes
- Round monetary values to 2 decimal places
- Round percentages to 1 decimal place
- Sort all output tables alphabetically by metric name unless otherwise specified
