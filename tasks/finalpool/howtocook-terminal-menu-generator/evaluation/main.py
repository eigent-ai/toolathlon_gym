"""
Evaluation for howtocook-terminal-menu-generator task.

Checks:
1. Weekly_Menu.docx exists and is readable
2. Has at least 5 sections (one per weekday Mon-Fri)
3. Contains dish names from at least 4 different categories
4. Each weekday section has ingredients listed
5. Memory file has been updated with entities
"""
import json
import os
import re
import sys
from argparse import ArgumentParser
from datetime import datetime

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {name}: {detail}")


def main():
    global PASS_COUNT, FAIL_COUNT

    parser = ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    agent_ws = args.agent_workspace

    # ---- Check 1: Weekly_Menu.docx exists and is readable ----
    docx_path = os.path.join(agent_ws, "Weekly_Menu.docx")
    if not os.path.exists(docx_path):
        check("Weekly_Menu.docx exists", False, f"Not found at {docx_path}")
        # Cannot continue without the file
        print(f"\nResults: {PASS_COUNT}/{PASS_COUNT + FAIL_COUNT} passed, {FAIL_COUNT} failed")
        sys.exit(1)

    try:
        from docx import Document
        doc = Document(docx_path)
        all_paragraphs = [p.text for p in doc.paragraphs]
        full_text = "\n".join(all_paragraphs)
        check("Weekly_Menu.docx exists and is readable", True)
    except Exception as e:
        check("Weekly_Menu.docx exists and is readable", False, str(e))
        print(f"\nResults: {PASS_COUNT}/{PASS_COUNT + FAIL_COUNT} passed, {FAIL_COUNT} failed")
        sys.exit(1)

    normalized = full_text.lower()

    # ---- Check 2: Has at least 5 weekday sections ----
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    found_days = [d for d in weekdays if d in normalized]
    check("Has at least 5 weekday sections (Mon-Fri)",
          len(found_days) >= 5,
          f"Found {len(found_days)} weekday(s): {found_days}")

    # ---- Check 3: Contains dishes from at least 4 different categories ----
    # Look for category keywords in the document
    category_keywords = {
        "meat": ["meat", "chicken", "pork", "beef", "lamb", "duck",
                 "wings", "ribs",
                 "\u8089", "\u9e21", "\u7fc5", "\u732a", "\u725b", "\u7f8a", "\u9e2d"],
        "vegetable": ["vegetable", "veggie", "tofu", "mushroom", "bean",
                       "greens", "salad", "cabbage", "eggplant",
                       "\u83dc", "\u8c46", "\u83c7", "\u7d20", "\u8304",
                       "\u91d1\u9488\u83c7", "\u51c9\u62cc"],
        "soup": ["soup", "broth", "stew",
                 "\u6c64", "\u7092"],
        "staple": ["rice", "noodle", "bread", "cake", "dumpling",
                   "pancake", "bun",
                   "\u996d", "\u9762", "\u997c", "\u5e74\u7cd5",
                   "\u7c89", "\u9985"],
        "seafood": ["fish", "shrimp", "prawn", "crab", "squid",
                    "\u9c7c", "\u867e", "\u87f9"],
        "snack": ["snack", "dessert", "sweet", "cookie",
                  "\u70b9\u5fc3", "\u96f6\u98df", "\u751c"],
    }

    found_categories = set()
    for cat, keywords in category_keywords.items():
        for kw in keywords:
            if kw in normalized:
                found_categories.add(cat)
                break

    check("Contains dishes from at least 4 different categories",
          len(found_categories) >= 4,
          f"Found {len(found_categories)} categories: {found_categories}")

    # ---- Check 4: Each weekday section has ingredients ----
    # Check that ingredient-related words appear multiple times
    ingredient_indicators = ["ingredient", "ingredients",
                             "\u539f\u6599", "\u6750\u6599", "\u98df\u6750",
                             "salt", "oil", "sugar", "sauce", "water",
                             "garlic", "ginger", "onion", "pepper",
                             "\u76d0", "\u6cb9", "\u7cd6", "\u916b", "\u6c34",
                             "\u849c", "\u59dc", "\u8471", "\u6912"]
    ingredient_count = 0
    for indicator in ingredient_indicators:
        ingredient_count += normalized.count(indicator)

    check("Weekday sections contain ingredient information",
          ingredient_count >= 5,
          f"Found only {ingredient_count} ingredient-related terms")

    # ---- Check 5: Document has sufficient content ----
    check("Document has sufficient content (>= 500 chars)",
          len(full_text.strip()) >= 500,
          f"Only {len(full_text.strip())} characters")

    # ---- Check 6: Memory file has been updated ----
    memory_path = os.path.join(agent_ws, "memory", "memory.json")
    if os.path.exists(memory_path):
        try:
            with open(memory_path) as f:
                mem_data = json.load(f)
            entities = mem_data.get("entities", [])
            check("Memory file has been updated with entities",
                  len(entities) > 0,
                  "No entities found in memory.json")
        except Exception as e:
            check("Memory file has been updated with entities", False, str(e))
    else:
        check("Memory file has been updated with entities", False,
              f"memory.json not found at {memory_path}")

    # ---- Summary ----
    total = PASS_COUNT + FAIL_COUNT
    print(f"\nResults: {PASS_COUNT}/{total} passed, {FAIL_COUNT} failed")

    if args.res_log_file:
        result = {
            "total_passed": PASS_COUNT,
            "total_checks": total,
            "accuracy": (PASS_COUNT / total * 100) if total > 0 else 0,
            "timestamp": datetime.now().isoformat(),
        }
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    sys.exit(0 if FAIL_COUNT == 0 else 1)


if __name__ == "__main__":
    main()
