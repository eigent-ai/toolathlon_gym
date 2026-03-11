I am designing a corporate wellness meal program for our company. First, look up recipes from our recipe database covering different categories like breakfast, lunch options, and healthy side dishes. Get at least 10 recipes with their ingredients and nutritional information.

There is a wellness program API at http://localhost:30343/api/wellness_guidelines.json that has dietary guidelines including daily calorie targets, macro ratios, and food group recommendations. Please fetch that data.

Use the terminal to create and run a Python script called wellness_planner.py in the workspace that reads recipes.json and wellness_guidelines.json (create both first), evaluates each recipe against the dietary guidelines, calculates nutritional compliance scores, creates a weekly meal plan, and outputs wellness_plan.json.

Create an Excel file called Corporate_Wellness_Plan.xlsx with four sheets. The first sheet Recipe_Evaluation should have columns Recipe_Name, Category, Difficulty, Ingredient_Count, Estimated_Calories, and Wellness_Score (1-10, round to 1 decimal), sorted by Wellness_Score descending. The second sheet Weekly_Plan should have columns Day (Monday through Friday), Breakfast, Lunch, and Snack with recommended recipe names. The third sheet Nutritional_Summary should have columns Meal_Slot, Avg_Calories, Protein_Pct, Carb_Pct, Fat_Pct with estimated macro breakdowns. The fourth sheet Program_Metrics should have Metric and Value columns with Total_Recipes_Evaluated, Recipes_Meeting_Guidelines, Weekly_Avg_Calories, Program_Compliance_Pct (round to 1 decimal), and Recommended_Budget_Per_Person (round to 2 decimals).

Create a Word document called Wellness_Program_Guide.docx with heading "Corporate Wellness Meal Program", sections for "Program Overview", "Weekly Meal Plans", "Nutritional Guidelines Compliance", and "Implementation Recommendations".

Schedule a calendar event "Wellness Program Launch" on March 18, 2026 from 12:00 PM to 1:00 PM UTC with description covering program highlights and first week menu.
