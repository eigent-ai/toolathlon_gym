# Segment Analysis Methodology

## Core Metrics
- Customer Count: COUNT(DISTINCT CUSTOMER_ID) per segment
- Total Orders: COUNT(ORDER_ID) per segment
- Total Revenue: SUM(TOTAL_AMOUNT), round to 2 decimals
- Avg Order Value: AVG(TOTAL_AMOUNT), round to 2 decimals
- Orders Per Customer: Total Orders / Customer Count, round to 2 decimals
- Avg Discount Pct: AVG(DISCOUNT) * 100, round to 2 decimals
- Revenue Share: segment revenue / total revenue * 100, round to 1 decimal

## Profitability Index
Formula: AVG((UNIT_PRICE - UNIT_COST) / UNIT_PRICE * 100)
Round to 1 decimal place. Requires joining orders with products table.

## Growth Indicators
1. Find the midpoint of the order date range (MIN to MAX date)
2. Count orders in each half for each segment
3. High Growth: > 50% of orders fall in the recent half
4. Low Growth: <= 50% of orders in the recent half

## Strategic Categories
Based on BCG Matrix methodology:
- Compare each segment's revenue contribution to the median across segments
- Star: above-median revenue + high growth
- Cash Cow: above-median revenue + low growth
- Question Mark: below-median revenue + high growth
- Dog: below-median revenue + low growth
