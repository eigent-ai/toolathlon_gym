"""
Preprocess script for howtocook-survey-analysis task.

Clears writable schemas and injects:
1. A Google Form "Team Lunch Preference Survey" with 5 questions
2. 12 form responses with varied taste preferences
"""

import argparse
import json
import os

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def clear_all(cur):
    """Clear all writable schemas in FK-safe order."""
    print("[preprocess] Clearing all writable schemas...")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    cur.execute("DELETE FROM gcal.events")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    cur.execute("DELETE FROM notion.users")
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.sheets")
    cur.execute("DELETE FROM gsheet.spreadsheets")
    print("[preprocess] All schemas cleared.")


def inject_form_data(cur):
    """Inject the Team Lunch Preference Survey form and 12 responses."""
    print("[preprocess] Injecting form data...")

    form_id = "form-lunch-survey-001"
    q_name = "q-name-001"
    q_cuisine = "q-cuisine-001"
    q_spice = "q-spice-001"
    q_allergy = "q-allergy-001"
    q_difficulty = "q-difficulty-001"

    # Create form
    cur.execute(
        """INSERT INTO gform.forms (id, title, document_title, description)
           VALUES (%s, %s, %s, %s)""",
        (form_id, "Team Lunch Preference Survey", "Team Lunch Preference Survey",
         "Help us plan the next team lunch by sharing your taste preferences."),
    )

    # Create questions
    questions = [
        (q_name, form_id, "Your Name", "textQuestion", True, "{}", 0),
        (
            q_cuisine, form_id, "Preferred cuisine type", "choiceQuestion", True,
            json.dumps({
                "type": "RADIO",
                "options": [
                    {"value": "荤菜"},
                    {"value": "素菜"},
                    {"value": "水产"},
                    {"value": "主食"},
                    {"value": "甜品"},
                ],
            }),
            1,
        ),
        (
            q_spice, form_id, "Spice tolerance", "choiceQuestion", True,
            json.dumps({
                "type": "RADIO",
                "options": [
                    {"value": "Mild"},
                    {"value": "Medium"},
                    {"value": "Spicy"},
                ],
            }),
            2,
        ),
        (q_allergy, form_id, "Any food allergies?", "textQuestion", False, "{}", 3),
        (
            q_difficulty, form_id, "Max cooking difficulty you'd accept (1-5)", "choiceQuestion", True,
            json.dumps({
                "type": "RADIO",
                "options": [
                    {"value": "1"},
                    {"value": "2"},
                    {"value": "3"},
                    {"value": "4"},
                    {"value": "5"},
                ],
            }),
            4,
        ),
    ]

    for q in questions:
        cur.execute(
            """INSERT INTO gform.questions
               (id, form_id, title, question_type, required, config, position)
               VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)""",
            q,
        )

    # 12 responses
    # 荤菜=6, 素菜=2, 主食=2, 水产=1, 甜品=1
    responses = [
        ("Alice", "alice@company.com", "荤菜", "Medium", "None", "3"),
        ("Bob", "bob@company.com", "素菜", "Mild", "Peanut", "2"),
        ("Carol", "carol@company.com", "荤菜", "Spicy", "None", "4"),
        ("David", "david@company.com", "主食", "Medium", "None", "2"),
        ("Eva", "eva@company.com", "荤菜", "Medium", "Shellfish", "3"),
        ("Frank", "frank@company.com", "水产", "Mild", "None", "2"),
        ("Grace", "grace@company.com", "素菜", "Mild", "None", "1"),
        ("Henry", "henry@company.com", "荤菜", "Spicy", "None", "5"),
        ("Iris", "iris@company.com", "甜品", "Mild", "Dairy", "2"),
        ("Jack", "jack@company.com", "荤菜", "Medium", "None", "3"),
        ("Karen", "karen@company.com", "主食", "Medium", "Gluten", "3"),
        ("Leo", "leo@company.com", "荤菜", "Spicy", "None", "4"),
    ]

    for name, email, cuisine, spice, allergy, difficulty in responses:
        answers = json.dumps({
            q_name: name,
            q_cuisine: cuisine,
            q_spice: spice,
            q_allergy: allergy,
            q_difficulty: difficulty,
        })
        cur.execute(
            """INSERT INTO gform.responses (form_id, respondent_email, answers)
               VALUES (%s, %s, %s::jsonb)""",
            (form_id, email, answers),
        )

    print(f"[preprocess] Injected form with {len(questions)} questions and {len(responses)} responses.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_all(cur)
        inject_form_data(cur)
        conn.commit()
        print("[preprocess] Database operations committed.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Database error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
