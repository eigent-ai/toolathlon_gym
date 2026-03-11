I am planning a weekly office lunch menu and need your help pulling together recipes, filtering them, and producing a polished document.

Start by searching the recipe database for dishes across at least four different categories. Browse through the available categories and collect a good variety of options including meat dishes, vegetable dishes, soups, and staple foods or snacks. For each recipe you find, note its name, category, difficulty rating, and the list of ingredients.

Once you have gathered a sufficient pool of recipes, save them as a JSON file called all_recipes.json in the workspace. Each entry should have fields for name, category, difficulty, and ingredients. Then run the provided filter_recipes.py script to filter this collection, keeping only recipes whose difficulty is 3 or below. Save the filtered output to a file called filtered_recipes.json in the workspace.

Before selecting your final dishes, please remember these dietary preferences for future reference: no dishes with difficulty above 3, prefer variety across categories, aim for at least one soup and one vegetable dish during the week, and avoid repeating categories on consecutive days. Also remember the names of the dishes you ultimately select so they can be referenced later.

From the filtered results, pick five dishes for the weekday menu, one per day from Monday through Friday. Make sure they span at least four distinct categories and respect the dietary preferences you recorded.

Finally, generate a Word document called Weekly_Menu.docx in the workspace. The document should have a title heading of Weekly Lunch Menu. Then for each weekday from Monday through Friday, add a section heading with the day name. Under each day, include the dish name, its category, its difficulty level, and a complete list of ingredients for that dish. At the end of the document, add a section with any notes about the dietary preferences that guided your selections.
