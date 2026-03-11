The company cafeteria manager needs to estimate costs for adding Chinese dishes to the weekly menu. A grocery price list is available in the file grocery_prices.json in your workspace, containing current market prices for common Chinese cooking ingredients with both English and Chinese names.

Please browse the recipe database and select 5 dishes from different categories. For each dish, identify the required ingredients from the recipe and match them to prices in the grocery_prices.json file. Since recipe ingredients may be in Chinese and the price list includes both English and Chinese names, use the Chinese name field for matching where possible.

Create an Excel file called Recipe_Cost_Analysis.xlsx in your workspace with three sheets.

The first sheet should be named "Dish Costs" and should have columns Dish_Name, Ingredient_List (comma-separated list of matched ingredients), Estimated_Total_Cost (sum of matched ingredient prices), and Cost_Per_Serving (assuming 4 servings per recipe, divide total cost by 4 and round to 2 decimal places). Include one row per dish for a total of 5 rows.

The second sheet should be named "Ingredient Prices" and should have columns Ingredient_Name, Unit, Price_Per_Unit, and Source_Dish (which dishes use this ingredient, comma-separated if multiple). Include one row for each unique ingredient that was matched across all dishes.

The third sheet should be named "Budget Summary" and should have columns Metric and Value with the following entries: Total_Cost (sum of all dish costs), Average_Cost_Per_Dish (total divided by 5, rounded to 2 decimal places), Cheapest_Dish (name of the dish with lowest estimated cost), and Most_Expensive_Dish (name of the dish with highest estimated cost).

Finally, create a Google Sheet spreadsheet titled "Cafeteria Menu Cost Analysis" containing the Dish Costs data with the same columns so the information can be easily shared with the procurement team.
