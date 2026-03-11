"""Preprocess for terminal-wc-howtocook-gform-excel-notion.
Clears gform, notion. Injects survey form with questions and sample responses. Injects noise data."""
import argparse
import json
import os
import uuid
import glob as globmod

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear gform
        cur.execute("DELETE FROM gform.responses")
        cur.execute("DELETE FROM gform.questions")
        cur.execute("DELETE FROM gform.forms")
        print("[preprocess] Cleared gform data.")

        # Clear notion
        cur.execute("DELETE FROM notion.comments")
        cur.execute("DELETE FROM notion.blocks")
        cur.execute("DELETE FROM notion.pages")
        cur.execute("DELETE FROM notion.databases")
        print("[preprocess] Cleared notion data.")

        # ---- Inject the survey form with questions and responses ----
        form_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gform.forms (id, title, document_title, description, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (form_id, "Meal Kit Interest Survey", "Meal Kit Interest Survey",
              "Survey to gauge customer interest in meal kit products bundled with kitchen appliances."))

        questions = [
            ("How often do you cook at home?", "RADIO",
             {"options": ["Daily", "Several times a week", "Once a week", "Rarely"]}),
            ("What cuisine types interest you most?", "RADIO",
             {"options": ["Chinese", "Japanese", "Western", "Southeast Asian", "All types"]}),
            ("Which kitchen appliances do you currently own?", "CHECKBOX",
             {"options": ["Blender", "Vacuum Sealer", "Electric Cooker", "Kitchen Scale", "Exhaust Fan", "None"]}),
            ("What is your monthly budget for meal kits?", "RADIO",
             {"options": ["Under 30 dollars", "30 to 60 dollars", "60 to 100 dollars", "Over 100 dollars"]}),
            ("How likely are you to purchase a meal kit bundled with an appliance?", "SCALE",
             {"low": 1, "high": 5, "low_label": "Not likely", "high_label": "Very likely"}),
            ("What features would make a meal kit most appealing to you?", "TEXT", {}),
        ]
        q_ids = []
        for i, (title, qtype, config) in enumerate(questions):
            qid = str(uuid.uuid4())
            q_ids.append(qid)
            cur.execute("""
                INSERT INTO gform.questions (id, form_id, item_id, title, question_type, required, config, position)
                VALUES (%s, %s, %s, %s, %s, true, %s::jsonb, %s)
            """, (qid, form_id, str(uuid.uuid4()), title, qtype, json.dumps(config), i))

        # Inject 25 sample survey responses
        response_data = [
            ["Daily", "Chinese", ["Blender", "Electric Cooker"], "30 to 60 dollars", "4", "Easy recipes with fresh ingredients"],
            ["Several times a week", "Chinese", ["Blender"], "30 to 60 dollars", "5", "Quick prep time"],
            ["Several times a week", "Japanese", ["Kitchen Scale"], "60 to 100 dollars", "4", "Variety of cuisines"],
            ["Several times a week", "Chinese", ["Blender", "Kitchen Scale"], "30 to 60 dollars", "3", "Healthy options"],
            ["Daily", "All types", ["Blender", "Vacuum Sealer", "Electric Cooker"], "60 to 100 dollars", "5", "Organic ingredients"],
            ["Once a week", "Western", ["Exhaust Fan"], "Under 30 dollars", "3", "Easy recipes with fresh ingredients"],
            ["Several times a week", "Chinese", ["Electric Cooker"], "30 to 60 dollars", "4", "Step-by-step instructions"],
            ["Several times a week", "Chinese", ["Blender", "Exhaust Fan"], "30 to 60 dollars", "4", "Fresh ingredients"],
            ["Daily", "Chinese", ["Vacuum Sealer", "Electric Cooker"], "60 to 100 dollars", "5", "Easy recipes with fresh ingredients"],
            ["Several times a week", "Southeast Asian", ["Blender"], "30 to 60 dollars", "4", "Unique recipes"],
            ["Several times a week", "Chinese", ["Kitchen Scale", "Electric Cooker"], "30 to 60 dollars", "3", "Affordable kits"],
            ["Several times a week", "Chinese", ["Blender", "Vacuum Sealer"], "30 to 60 dollars", "4", "Easy recipes with fresh ingredients"],
            ["Rarely", "Western", ["None"], "Under 30 dollars", "2", "Simple instructions"],
            ["Once a week", "Chinese", ["Electric Cooker"], "30 to 60 dollars", "4", "Fresh ingredients"],
            ["Several times a week", "Chinese", ["Blender"], "30 to 60 dollars", "5", "Easy recipes with fresh ingredients"],
            ["Daily", "Japanese", ["Kitchen Scale", "Blender"], "60 to 100 dollars", "4", "Premium ingredients"],
            ["Several times a week", "Chinese", ["Exhaust Fan", "Electric Cooker"], "30 to 60 dollars", "4", "Quick prep time"],
            ["Once a week", "All types", ["Blender"], "Under 30 dollars", "3", "Budget friendly"],
            ["Several times a week", "Chinese", ["Vacuum Sealer"], "30 to 60 dollars", "4", "Easy recipes with fresh ingredients"],
            ["Daily", "Chinese", ["Blender", "Electric Cooker", "Kitchen Scale"], "Over 100 dollars", "5", "Complete meal solutions"],
            ["Several times a week", "Southeast Asian", ["Exhaust Fan"], "30 to 60 dollars", "4", "Authentic recipes"],
            ["Once a week", "Chinese", ["Electric Cooker"], "Under 30 dollars", "3", "Easy recipes with fresh ingredients"],
            ["Several times a week", "Chinese", ["Blender", "Vacuum Sealer"], "60 to 100 dollars", "4", "Fresh ingredients"],
            ["Several times a week", "Western", ["Kitchen Scale"], "30 to 60 dollars", "3", "Baking recipes"],
            ["Daily", "Chinese", ["Blender", "Exhaust Fan"], "30 to 60 dollars", "5", "Easy recipes with fresh ingredients"],
        ]
        for resp_data in response_data:
            answers = {}
            for j, qid in enumerate(q_ids):
                val = resp_data[j]
                if isinstance(val, list):
                    answers[qid] = val
                else:
                    answers[qid] = str(val)
            cur.execute("""
                INSERT INTO gform.responses (id, form_id, respondent_email, answers, create_time, last_submitted_time)
                VALUES (%s, %s, %s, %s::jsonb, NOW(), NOW())
            """, (str(uuid.uuid4()), form_id,
                  f"customer{response_data.index(resp_data)+1}@example.com",
                  json.dumps(answers)))

        print("[preprocess] Injected survey form with 6 questions and 25 responses.")

        # ---- Inject noise gform ----
        noise_form_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO gform.forms (id, title, document_title, description, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (noise_form_id, "Website Redesign Feedback", "Website Redesign Feedback",
              "Archived survey about website redesign preferences."))
        cur.execute("""
            INSERT INTO gform.questions (id, form_id, item_id, title, question_type, required, position)
            VALUES (%s, %s, %s, %s, %s, true, 0)
        """, (str(uuid.uuid4()), noise_form_id, str(uuid.uuid4()),
              "Rate the new website design", "SCALE"))
        print("[preprocess] Injected noise gform data.")

        # ---- Inject noise notion data ----
        noise_db_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notion.databases (id, title, description, properties, parent, created_time, last_edited_time)
            VALUES (%s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb, NOW(), NOW())
        """, (noise_db_id,
              json.dumps([{"type": "text", "text": {"content": "Q1 Sprint Backlog"}}]),
              json.dumps([{"type": "text", "text": {"content": "Engineering sprint tasks"}}]),
              json.dumps({"Title": {"id": "title", "type": "title", "title": {}}}),
              json.dumps({"type": "workspace", "workspace": True})))
        for i in range(3):
            page_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notion.pages (id, parent, properties, created_time, last_edited_time)
                VALUES (%s, %s::jsonb, %s::jsonb, NOW(), NOW())
            """, (page_id,
                  json.dumps({"type": "database_id", "database_id": noise_db_id}),
                  json.dumps({"Title": {"title": [{"text": {"content": f"Sprint Task {i+1}"}}]}})))
        print("[preprocess] Injected noise notion data.")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    if args.agent_workspace:
        for pattern in ["Meal_Kit_Analysis.xlsx", "appliance_recipe_matcher.py",
                        "survey_analyzer.py", "appliance_recipe_matches.json"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
