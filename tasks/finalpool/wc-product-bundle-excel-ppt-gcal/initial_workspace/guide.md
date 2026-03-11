# Product Bundling Analysis Guide

## Extracting Co-Purchase Data

Product co-purchase analysis identifies products that customers frequently buy together in the same order. The data source is the order line items, where each order may contain multiple products.

### Methodology

1. **Extract order line items**: Each order contains a `line_items` field (JSONB array) with entries like `{"product_id": 16, "name": "Canon M50...", "quantity": 1, "price": 698.67}`.

2. **Filter valid orders**: Only include orders with status 'completed' or 'processing'.

3. **Generate product pairs**: For each order with 2+ distinct products, generate all unique pairs (A, B) where A's product_id < B's product_id to avoid duplicates.

4. **Count co-occurrences**: Count how many orders each product pair appears in together. This is the co-purchase count.

5. **Calculate revenue metrics**: For each pair, compute the average combined revenue (sum of both products' prices in orders where they co-occur).

### Priority Scoring

Priority Score = Co_Purchase_Count * Avg_Combined_Revenue

This metric balances purchase frequency with revenue potential. Higher scores indicate bundles that are both popular and profitable.

### Category Insights

Track which product categories participate most actively in bundles. Calculate:
- Number of unique products from each category appearing in any bundle
- Bundle participation rate: percentage of a category's total products that appear in bundles
- Top bundle partner category: which other category most frequently pairs with products from this category
