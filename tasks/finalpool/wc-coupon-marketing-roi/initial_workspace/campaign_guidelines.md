Campaign Performance Guidelines

Minimum ROI Threshold: 200%
ROI Calculation: ((Revenue from coupon orders - Campaign budget) / Campaign budget) * 100

Target Conversion Rate: 3% (orders / clicks * 100)

Campaign Data API: http://localhost:30204/api/campaigns.json

Analysis Steps:
1. Fetch campaign data from the API
2. For each campaign with a coupon code, look up the coupon in the store
3. Use the coupon's usage_count as the number of orders generated
4. Calculate revenue by multiplying usage_count by average order value
5. Since we cannot track exact revenue per coupon from order data,
   use a simulated revenue = usage_count * 50 (average order value estimate)
6. Calculate ROI and conversion rate for each campaign
7. Only analyze campaigns that have a valid coupon code

Google Form: Create a survey for team feedback on campaign effectiveness.
