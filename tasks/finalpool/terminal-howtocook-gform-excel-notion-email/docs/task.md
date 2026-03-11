You are a corporate wellness coordinator responsible for launching an employee lunch program. Your goal is to create a dietary preference survey, select recipes that match common employee preferences, plan a weekly menu, build a recipe knowledge base, and communicate the program to staff.

Start by reading the Cafeteria_Budget.pdf in your workspace, which describes the budget per meal and expected headcount. Also review the dietary_requirements.json file that lists common dietary restrictions and allergen considerations for the employee population.

Create a dietary preference survey using the forms platform. The survey should be titled "Employee Lunch Program Preferences" and include the following five questions: a multiple choice question asking about preferred cuisine type with options Chinese Meat Dishes, Chinese Vegetable Dishes, Chinese Staple Foods, Soups, and Seafood; a multiple choice question about spice tolerance with options Mild, Medium, and Spicy; a checkbox question about dietary restrictions with options Vegetarian, No Pork, No Seafood, Gluten Free, and No Restrictions; a scale question from 1 to 5 asking how important variety is in their lunch options; and a short text question for any additional food preferences or allergies.

Query the recipe database to find recipes across different categories. Search for at least two meat dishes, two vegetable dishes, one staple food, one soup, and one seafood dish. For each recipe retrieved, note the recipe name, category, difficulty level, and ingredients list.

Write a Python script called menu_planner.py in your workspace and execute it using command-line tools. The script should select five recipes for a Monday through Friday weekly menu, choosing recipes that balance different categories (no two consecutive days with the same category) and keeping difficulty at 4 or below for cafeteria feasibility. The script should estimate a cost per serving of 8 dollars for meat and seafood dishes, 5 dollars for vegetable dishes, 6 dollars for staple foods, and 4 dollars for soups, then compute the total weekly cost assuming 50 servings per day.

Create an Excel workbook called Meal_Program_Plan.xlsx in your workspace with four sheets.

The first sheet should be named Survey_Questions and contain columns for question_num, text, and type. Include one row for each of the five survey questions.

The second sheet should be named Recipe_Selection and contain columns for recipe_name, category, and difficulty. Include one row for each recipe you retrieved from the recipe database, with at least seven recipes total.

The third sheet should be named Weekly_Menu and contain columns for day, lunch_recipe, and estimated_cost. Include five rows, one for each weekday Monday through Friday, with the assigned recipe and estimated cost per serving.

The fourth sheet should be named Program_Summary and contain columns for metric and value. Include rows for total_weekly_cost (sum of daily cost times 50 servings), avg_daily_cost_per_person, survey_question_count (5), recipes_evaluated (total recipes retrieved), and menu_days (5).

Set up a database in the team wiki system called "Recipe Knowledge Base" with properties for Recipe Name (title), Category (select with options for the main recipe categories), Difficulty (number), and Suitable For (multi-select with options Lunch, Dinner, Quick Meal). Add one entry for each recipe you included in the weekly menu.

Send an email to all_staff@company.com with the subject "New Employee Lunch Program - Take Our Survey" describing the new lunch program, mentioning that the weekly menu has been planned with a variety of dishes, and encouraging employees to fill out the dietary preference survey to help improve future menu selections.
