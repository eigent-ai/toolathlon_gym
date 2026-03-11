# Escalation Policy for Product Quality Issues

## Overview
When a product is identified as having systemic quality issues across multiple data sources, it must be escalated according to the severity classification.

## Severity Levels

### Critical
Products whose severity score exceeds the 80th percentile of all identified problem products. These require immediate attention from the Quality Team and should be tracked in the team knowledge base with Status set to Open.

### High
Products with severity score at or above 50. These should be reviewed within 5 business days.

### Medium
Products with severity score between 25 and 49. Monthly review cycle.

### Low
Products with severity score below 25. Quarterly review cycle.

## Escalation Contacts
- Quality Team Lead: quality_lead@company.com
- Product Team: product_team@company.com
- Support Team: support_team@company.com
- VP Customer Experience: vp_cx@company.com

## Process
1. Identify problem products from e-commerce refund/failure data and customer reviews
2. Cross-reference with support center ticket data for additional context
3. Compute severity scores using the weighted formula in audit_criteria.json
4. Create tracking entries for critical items
5. Notify relevant teams via email with findings summary
