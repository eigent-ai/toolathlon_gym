# Refund Root Cause Analysis Methodology

## Overview
This guide outlines the methodology for investigating refund patterns and identifying root causes by cross-referencing refund data with product reviews.

## Step 1: Data Collection
- Pull all refund records including refund ID, order ID, amount, reason, and date.
- For each refunded order, identify the products involved from the order line items.
- Collect product review data (ratings and review text) for all refunded products.

## Step 2: Severity Classification
Classify each refund by severity based on the refund amount:
- **Critical**: Refund amount greater than $50
- **Major**: Refund amount between $20 and $50 (inclusive of $20)
- **Minor**: Refund amount less than $20

## Step 3: Issue Type Determination
For each refunded product, determine the issue type:
- Calculate the average review rating from all product reviews.
- If the product has refunds AND average rating < 3.0 → **Quality Issue**
- If the product has refunds AND average rating >= 3.0 → **Service Issue**
- If the product has refunds but no reviews → **No Reviews**

## Step 4: Root Cause Mapping
Map refund reasons to root cause categories:
- "Product defective" → Manufacturing Defect
- "Product arrived damaged" → Shipping Damage
- "Wrong item received" → Wrong Item
- "Changed my mind" or "Item not as described" → Customer Expectations
- "Duplicate order" or other → Other

## Step 5: Investigation Flagging
Products with 2 or more refunds require formal supplier investigation.

## Step 6: Reporting
- Create Excel workbook with Refund Details, Product Impact, and Summary sheets.
- Write Word document with Executive Summary, Trend Analysis, Product Findings, Root Cause Classification, Recommendations, and Action Plan.
- Email findings to quality team and supplier relations.
