You are a logistics coordinator for an online retail store. Your manager has asked you to conduct a shipping cost audit to determine whether the store is undercharging customers for shipping relative to actual carrier rates. The carrier rate tables are published online at http://localhost:30201/index.html which has links to both domestic and international rate pages.

Begin by reviewing the shipping guidelines document and the carrier contracts CSV file in your workspace. The shipping guidelines explain the store's flat rate shipping charges and specify how to determine the actual carrier cost for comparison purposes. Pay attention to the weight range assumption and which carrier rates to use for each shipping method.

Retrieve all orders from your online store that have a shipping charge greater than zero. For each order, note the order ID, order status, order total, shipping amount charged to the customer, and the shipping method used such as Standard Shipping or Express Shipping.

Next, fetch the carrier rate tables from the website. Navigate to the domestic rates page to find rates for FedEx, UPS, and USPS across different weight ranges and service levels. Per the guidelines, use the 5 to 10 lbs weight range for all orders. For orders shipped via Standard Shipping, use the USPS standard rate as the actual cost. For orders shipped via Express Shipping, use the FedEx express rate as the actual cost. For any orders with other shipping methods, use the USPS standard rate as a default.

Calculate the difference between the actual carrier cost and the amount charged to the customer for each order. An order is considered undercharged when the actual cost exceeds the amount charged.

Create an Excel file called Shipping_Audit.xlsx in your workspace with three sheets. The first sheet should be named "Rate Comparison" with columns Order_ID, Status, Order_Total, Shipping_Charged, Shipping_Method, Carrier, Actual_Cost, Difference, and Undercharged where Undercharged is either Yes or No. Include every order that has a shipping charge. The second sheet should be named "Undercharged Orders" with columns Order_ID, Status, Order_Total, Shipping_Charged, Actual_Cost, and Difference, listing only the orders where shipping was undercharged. The third sheet should be named "Summary" with two columns Metric and Value containing Total_Orders_Analyzed, Undercharged_Count, Total_Undercharged_Amount, and Avg_Undercharge_Per_Order.

Send an email to logistics@company.com with the subject line "Shipping Cost Audit Alert" summarizing how many orders were undercharged, the total undercharged amount, and listing at least the first ten undercharged order IDs. The email should recommend reviewing the current flat rate shipping structure.

When you have completed all tasks, call claim_done.
