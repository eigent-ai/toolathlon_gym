# Market Intelligence Portal Guide

## API Endpoint
The market intelligence data is available at:
```
http://localhost:30195/api/market_data.json
```

## Data Format
The API returns a JSON object with:
- `market_overview`: Overall market size, year-over-year growth, and report date
- `categories`: Array of category-level data including market average price, market revenue, and growth rate

## Cross-Referencing Methodology
1. Fetch market data from the API endpoint
2. Query your own store's product catalog for product counts and average prices per category
3. Query order data to compute actual revenue per category
4. Compare own metrics against market benchmarks using the framework in Competitive_Strategy.pdf
