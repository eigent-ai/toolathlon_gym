# Supply Chain Management Policy

Inventory Management Rules:
- Safety stock factor: 1.5x lead time demand
- Reorder when stock falls below reorder point
- Minimum order quantities must be respected
- Prioritize suppliers with reliability > 80%

Risk Classification:
- Critical: Stock below reorder point
- Warning: Stock within 20% above reorder point
- Healthy: Stock well above reorder point

Daily sales rate = Total sales / 90 (assuming 90-day window)
Days until stockout = Current stock / daily sales rate
Reorder point = daily_sales_rate * lead_time * 1.5
