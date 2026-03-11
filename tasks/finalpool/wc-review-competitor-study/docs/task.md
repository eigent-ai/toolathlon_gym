You are a product quality analyst for an online store. You need to evaluate how your product reviews compare against industry competitor benchmarks and create a knowledge base summarizing your findings.

Start by reading the review strategy document and category mapping file in your workspace. The review strategy outlines the quality targets and analysis requirements. The category mapping file shows how your store categories correspond to the competitor benchmark categories.

The competitor review benchmark dashboard is available at http://localhost:30203/index.html with separate pages for each product category. Visit the dashboard and navigate to each category page to collect the competitor benchmark metrics including average rating, review count, and sentiment score.

Retrieve all product reviews from your online store. For each product category, calculate the average rating and total review count. Then compare your category averages against the competitor benchmark averages from the dashboard.

Create an Excel file called Review_Benchmark.xlsx in your workspace with three sheets. The first sheet should be named "Category Comparison" with columns Category, Our_Avg_Rating, Our_Review_Count, Competitor_Avg_Rating, Competitor_Review_Count, Rating_Difference, and Status. The Rating_Difference is your average minus the competitor average. The Status should be "Above" if you are higher, "Below" if you are lower, or "Equal" if they match.

The second sheet should be named "Products Below Benchmark" and list all individual products whose average rating falls below the competitor benchmark average for their category. Include columns Product_ID, Product_Name, Category, Our_Rating, Benchmark_Rating, and Gap where Gap is the benchmark minus our rating.

The third sheet should be named "Summary" with columns Metric and Value containing Total_Categories, Categories_Above_Benchmark, Categories_Below_Benchmark, and Products_Below_Benchmark.

Finally, create a Notion page titled "Review Performance Analysis Q1 2026" to serve as a knowledge base entry. The page should summarize the key findings from your analysis including which categories are performing above and below benchmark, how many products need improvement, and a brief recommendation for improving review scores in underperforming categories.

When you have completed all tasks, call claim_done.
