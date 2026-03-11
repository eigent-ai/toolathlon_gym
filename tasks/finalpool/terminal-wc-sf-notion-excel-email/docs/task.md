You are a Customer Experience analyst conducting a cross-platform support quality audit. The company runs an online e-commerce store and a separate internal support center, and the VP wants to understand where systemic quality issues exist by cross-referencing data from both systems.

Start by reading the audit_criteria.json file in your workspace. It defines the severity scoring formula, the quality thresholds, and the team contact information you will need later.

First, pull all orders from the e-commerce store that have a status of "refunded" or "failed". For each such order, extract the product IDs from the line items. Then pull all product reviews from the store that have a rating of 2 or below. These represent the products customers are most unhappy with.

Next, query the support center system for all tickets. Compute aggregated metrics grouped by priority level: the total number of tickets, average response time in hours, and average customer satisfaction score. Also query the support center for the list of support agents and their team assignments and skill levels.

Now write a Python script called correlate_issues.py in your workspace. This script should combine the e-commerce data to identify "problem products" meaning any product that appears in at least one refunded or failed order OR has at least one review with rating 2 or below. For each problem product, compute a severity score using the formula from audit_criteria.json: refund_count times the refund_weight (30) plus low_review_count times the review_weight (40). The script should output a file called problem_products.json containing a list of objects with product_id, product_name, category, refund_count, low_review_count, and severity_score, sorted by severity_score descending.

Write a second Python script called support_metrics.py in your workspace. This script should compute support center metrics by priority level: total ticket count, average response time hours rounded to two decimal places, and average customer satisfaction rounded to two decimal places. It should also compute issue type breakdown with ticket count and average satisfaction per issue type. Output the results to support_analysis.json.

Run both scripts via the terminal.

Create an Excel workbook called Support_Quality_Audit.xlsx in your workspace with four sheets.

The first sheet should be named Problem_Products with columns Product_ID, Product_Name, Category, Refund_Count, Low_Review_Count, and Severity_Score. Include all problem products sorted by Severity_Score descending. Only include the first 60 characters of product names if they are longer.

The second sheet should be named Support_By_Priority with columns Priority, Total_Tickets, Avg_Response_Hours, and Avg_Satisfaction. Include one row per priority level (High, Low, Medium) sorted alphabetically by priority name.

The third sheet should be named Issue_Type_Breakdown with columns Issue_Type, Ticket_Count, and Avg_Satisfaction. Include one row per issue type sorted by Ticket_Count descending.

The fourth sheet should be named Executive_Summary with columns Metric and Value. Include the following rows: Total Problem Products (the count of all problem products), Critical Products (count of products with severity score strictly above the 80th percentile of all severity scores), Total Support Tickets (total across all priorities), Overall Avg Satisfaction (average satisfaction across all tickets rounded to two decimals), Highest Risk Category (the category name that has the most problem products in it).

Create a knowledge base database called "Support Quality Tracker" with the following properties: Issue as the title property, Product as a rich text property, Severity as a select property with options Critical, High, Medium, and Low, Status as a select property with options Open, In Progress, and Resolved, and Assigned_To as a rich text property. Add one page entry for each of the top 6 problem products (those with severity score strictly above the 80th percentile). Set Issue to a description like "Quality issue - " followed by a short version of the product name. Set Product to the full product name (up to 60 characters). Set Severity to "Critical" for these entries. Set Status to "Open". Set Assigned_To to "Quality Team".

Send an email to support_team@company.com with subject "Support Quality Audit - Priority Analysis". The body should summarize the support center findings: ticket counts by priority, average satisfaction scores, and the issue types with lowest satisfaction. Include the overall average satisfaction score.

Send a second email to product_team@company.com with subject "Support Quality Audit - Problem Products Alert". The body should list the critical severity products (those above 80th percentile) with their names, refund counts, low review counts, and severity scores. Mention the total number of problem products identified and recommend investigation of the critical items.
