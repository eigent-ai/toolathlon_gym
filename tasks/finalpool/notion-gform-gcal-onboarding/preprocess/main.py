"""
Preprocess script for notion-gform-gcal-onboarding task.

Clears writable schemas and injects:
1. A Notion page "New Employee Onboarding Checklist" with 6 checklist blocks
2. A Google Form "New Employee Information" with 5 questions
3. 3 form responses (new hires: Sarah Park, Mike Chen, Amy Rodriguez)
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


def inject_notion_data(cur):
    """Inject the onboarding checklist page and blocks."""
    print("[preprocess] Injecting Notion data...")

    page_id = "page-onboarding-checklist-001"
    page_props = json.dumps({
        "title": {
            "id": "title",
            "type": "title",
            "title": [
                {
                    "type": "text",
                    "text": {"content": "New Employee Onboarding Checklist"},
                    "plain_text": "New Employee Onboarding Checklist",
                }
            ],
        }
    })

    cur.execute(
        """INSERT INTO notion.pages (id, object, parent, properties, url)
           VALUES (%s, 'page', '{"type": "workspace", "workspace": true}'::jsonb, %s, %s)""",
        (page_id, page_props, f"https://www.notion.so/{page_id}"),
    )

    checklist_items = [
        "Complete HR paperwork",
        "Set up workstation and accounts",
        "Meet team members",
        "Attend orientation session",
        "Review company handbook",
        "Complete compliance training",
    ]

    for i, item in enumerate(checklist_items):
        block_data = json.dumps({
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": item},
                    "plain_text": item,
                }
            ]
        })
        cur.execute(
            """INSERT INTO notion.blocks (parent_type, parent_id, type, block_data, position)
               VALUES ('page_id', %s, 'paragraph', %s::jsonb, %s)""",
            (page_id, block_data, i),
        )

    print(f"[preprocess] Injected Notion page with {len(checklist_items)} checklist blocks.")


def inject_form_data(cur):
    """Inject the new employee information form and 3 responses."""
    print("[preprocess] Injecting Google Form data...")

    form_id = "form-new-employee-001"
    q_name = "q-fullname-001"
    q_email = "q-email-001"
    q_dept = "q-department-001"
    q_start = "q-startdate-001"
    q_emergency = "q-emergency-001"

    # Create form
    cur.execute(
        """INSERT INTO gform.forms (id, title, document_title, description)
           VALUES (%s, %s, %s, %s)""",
        (
            form_id,
            "New Employee Information",
            "New Employee Information",
            "Please fill out your information before your start date.",
        ),
    )

    # Create questions
    questions = [
        (q_name, form_id, "Full Name", "textQuestion", True, "{}", 0),
        (q_email, form_id, "Email", "textQuestion", True, "{}", 1),
        (
            q_dept,
            form_id,
            "Department",
            "choiceQuestion",
            True,
            json.dumps(
                {
                    "type": "RADIO",
                    "options": [
                        {"value": "Engineering"},
                        {"value": "Sales"},
                        {"value": "Marketing"},
                        {"value": "HR"},
                    ],
                }
            ),
            2,
        ),
        (q_start, form_id, "Start Date", "textQuestion", True, "{}", 3),
        (q_emergency, form_id, "Emergency Contact", "textQuestion", True, "{}", 4),
    ]

    for q in questions:
        cur.execute(
            """INSERT INTO gform.questions
               (id, form_id, title, question_type, required, config, position)
               VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)""",
            q,
        )

    # 3 new hire responses
    responses = [
        ("Sarah Park", "sarah.park@company.com", "Engineering", "2026-03-16", "John Park: 555-0101"),
        ("Mike Chen", "mike.chen@company.com", "Sales", "2026-03-16", "Lisa Chen: 555-0202"),
        ("Amy Rodriguez", "amy.rodriguez@company.com", "Marketing", "2026-03-16", "Carlos Rodriguez: 555-0303"),
    ]

    for name, email, dept, start_date, emergency in responses:
        answers = json.dumps(
            {
                q_name: name,
                q_email: email,
                q_dept: dept,
                q_start: start_date,
                q_emergency: emergency,
            }
        )
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
        inject_notion_data(cur)
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
