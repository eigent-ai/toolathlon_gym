You are a marketing analyst for an online retail store. You need to evaluate the return on investment for each marketing campaign by linking campaign spending data with coupon redemption data from the store, and then create a feedback survey for the marketing team.

Begin by reviewing the marketing budget spreadsheet and campaign guidelines document in your workspace. The guidelines explain the ROI calculation formula, the minimum ROI threshold of 200 percent, the target conversion rate of 3 percent, and the revenue estimation methodology.

Fetch the campaign performance data from the API at http://localhost:30204/api/campaigns.json which returns a list of campaigns including campaign name, marketing channel, budget spent, impressions, clicks, and the coupon code associated with each campaign. Note that some campaigns may not have a coupon code or may reference codes not found in your store.

Next, retrieve all coupon data from your online store. For each coupon, note the code, discount type, discount amount, and usage count. The usage count represents the number of orders that used that coupon.

Link each campaign to its corresponding store coupon by matching the coupon code from the campaign data to the coupon code in the store. Only analyze campaigns that have a valid coupon code that exists in the store. Calculate revenue for each campaign as the coupon usage count multiplied by 50 dollars, which represents the estimated average order value. Compute the ROI percentage as revenue minus budget divided by budget times 100. Calculate the conversion rate as usage count divided by clicks times 100.

Create an Excel file called Campaign_ROI.xlsx in your workspace with three sheets. The first sheet named "Campaign Performance" should have columns Campaign_Name, Channel, Coupon_Code, Budget, Usage_Count, Revenue, ROI_Pct, Conversion_Rate, Meets_ROI_Target, and Meets_Conversion_Target. Set Meets_ROI_Target to Yes if ROI is 200 percent or above and No otherwise. Set Meets_Conversion_Target to Yes if the conversion rate is 3 percent or above and No otherwise.

The second sheet named "Channel Summary" should aggregate campaign data by marketing channel with columns Channel, Total_Budget, Total_Revenue, Channel_ROI_Pct, and Campaign_Count.

The third sheet named "Recommendations" should have two columns Category and Finding with rows for Campaigns Meeting ROI Target showing the count, Campaigns Below ROI Target showing the count, Best Channel by ROI naming the channel with highest ROI, and Worst Channel by ROI naming the channel with lowest ROI.

Create a Google Form titled "Campaign Effectiveness Feedback" to collect team input. The form should include a multiple choice question asking which marketing channel was most effective with options matching the channels from the campaign data, a short answer question asking for suggestions to improve campaign ROI, and a multiple choice question about preferred campaign frequency with options Monthly, Bi-weekly, Weekly, and Quarterly.

When you have completed all tasks, call claim_done.
