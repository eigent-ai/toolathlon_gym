"""
Preprocess for howtocook-weekly-gsheet-gcal task.

Injects a "Weekly Meal Plan" Google Sheet with 21 rows (7 days x 3 meals).
Injects 7 Google Calendar dinner prep events for April 7-13, 2026.
Clears email tables.

Prerequisites:
  - PostgreSQL toolathlon_gym database running on localhost:5432
"""
import os
import argparse
import json
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

# 21 meals: 7 days x 3 meals, based on actual HowToCook recipes
MEAL_PLAN = [
    # Day, Meal_Type, Recipe_Name (English), Prep_Time (min), Difficulty
    (1, "Breakfast", "Toast with Jam", 15, "Easy"),
    (1, "Lunch", "Stir-fried Vegetables", 30, "Medium"),
    (1, "Dinner", "Cola Chicken Wings", 30, "Medium"),
    (2, "Breakfast", "Sunny-side Up Egg", 15, "Easy"),
    (2, "Lunch", "Tomato Beef Egg Drop Soup", 60, "Hard"),
    (2, "Dinner", "Mapo Tofu", 30, "Medium"),
    (3, "Breakfast", "Oatmeal with Eggs", 15, "Easy"),
    (3, "Lunch", "Braised Pork Belly", 60, "Hard"),
    (3, "Dinner", "Steamed Eggs", 15, "Easy"),
    (4, "Breakfast", "Milk Oatmeal", 15, "Easy"),
    (4, "Lunch", "Cold Cucumber Salad", 15, "Easy"),
    (4, "Dinner", "Sweet and Sour Pork", 60, "Hard"),
    (5, "Breakfast", "Boiled Corn", 15, "Easy"),
    (5, "Lunch", "Noodle Soup", 30, "Medium"),
    (5, "Dinner", "Village Beer Duck", 60, "Hard"),
    (6, "Breakfast", "Scallion Pancake", 30, "Medium"),
    (6, "Lunch", "Cold Tofu", 15, "Easy"),
    (6, "Dinner", "Kung Pao Chicken", 30, "Medium"),
    (7, "Breakfast", "Steamed Soft Egg", 15, "Easy"),
    (7, "Lunch", "Cream of Mushroom Soup", 15, "Easy"),
    (7, "Dinner", "Stir-fried Pork with Garlic Sprouts", 30, "Medium"),
]

DINNER_RECIPES = {
    1: "Cola Chicken Wings",
    2: "Mapo Tofu",
    3: "Steamed Eggs",
    4: "Sweet and Sour Pork",
    5: "Village Beer Duck",
    6: "Kung Pao Chicken",
    7: "Stir-fried Pork with Garlic Sprouts",
}

GCAL_EVENTS = [
    {
        "summary": f"Dinner Prep - Day {day}",
        "description": f"Prepare dinner for Day {day}: {recipe}. Start cooking at 18:00.",
        "start": f"2026-04-{6 + day:02d} 18:00:00",
        "end": f"2026-04-{6 + day:02d} 19:00:00",
    }
    for day, recipe in DINNER_RECIPES.items()
]


def clear_tables(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gcal.events")
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        try:
            cur.execute("DELETE FROM email.drafts")
        except Exception:
            pass
    conn.commit()
    print("[preprocess] Cleared all target tables.")


def inject_gsheet(conn):
    with conn.cursor() as cur:
        # Create spreadsheet
        cur.execute("""
            INSERT INTO gsheet.spreadsheets (title)
            VALUES (%s)
            RETURNING id
        """, ("Weekly Meal Plan",))
        spreadsheet_id = cur.fetchone()[0]

        # Create sheet
        cur.execute("""
            INSERT INTO gsheet.sheets (spreadsheet_id, title, index, row_count, column_count)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (spreadsheet_id, "Meal Plan", 0, 25, 6))
        sheet_id = cur.fetchone()[0]

        # Insert header row
        headers = ["Day", "Meal_Type", "Recipe_Name", "Prep_Time", "Difficulty"]
        for col_idx, header in enumerate(headers):
            cur.execute("""
                INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value)
                VALUES (%s, %s, %s, %s, %s)
            """, (spreadsheet_id, sheet_id, 0, col_idx, header))

        # Insert data rows
        for row_idx, (day, meal_type, recipe, prep_time, difficulty) in enumerate(MEAL_PLAN, start=1):
            row_data = [str(day), meal_type, recipe, str(prep_time), difficulty]
            for col_idx, value in enumerate(row_data):
                cur.execute("""
                    INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value)
                    VALUES (%s, %s, %s, %s, %s)
                """, (spreadsheet_id, sheet_id, row_idx, col_idx, value))

    conn.commit()
    print(f"[preprocess] Injected 'Weekly Meal Plan' gsheet with {len(MEAL_PLAN)} data rows")


def inject_gcal_events(conn):
    with conn.cursor() as cur:
        for ev in GCAL_EVENTS:
            cur.execute("""
                INSERT INTO gcal.events (summary, description, start_datetime, end_datetime)
                VALUES (%s, %s, %s, %s)
            """, (ev["summary"], ev["description"], ev["start"], ev["end"]))
    conn.commit()
    print(f"[preprocess] Injected {len(GCAL_EVENTS)} dinner prep calendar events")


def ensure_email_folder(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")
            conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_tables(conn)
        inject_gsheet(conn)
        inject_gcal_events(conn)
        ensure_email_folder(conn)
    finally:
        conn.close()

    print("\n[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
