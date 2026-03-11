"""
Preprocess script for notion-team-survey-report task.

Clears writable schemas and injects:
1. A Notion page "Engineering Team Projects" with 5 project entries
2. A Google Form "Team Satisfaction Survey" with 4 rating questions
3. 8 survey responses rating Leadership, Workload, Communication, Growth (1-5)
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
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    cur.execute("DELETE FROM notion.users")
    print("[preprocess] All schemas cleared.")


def inject_notion_data(cur):
    """Inject the Engineering Team Projects page with 5 projects."""
    print("[preprocess] Injecting Notion data...")

    page_id = "page-eng-team-projects-001"
    page_props = json.dumps({
        "title": {
            "id": "title",
            "type": "title",
            "title": [
                {
                    "type": "text",
                    "text": {"content": "Engineering Team Projects", "link": None},
                    "plain_text": "Engineering Team Projects",
                }
            ],
        }
    })

    cur.execute(
        """INSERT INTO notion.pages (id, object, parent, properties, url)
           VALUES (%s, 'page', '{"type": "workspace", "workspace": true}'::jsonb, %s, %s)""",
        (page_id, page_props, f"https://www.notion.so/{page_id}"),
    )

    projects = [
        ("Project Alpha", "Active", "Alice Chen", "March 30, 2026",
         "Building the next-generation authentication system with OAuth 2.1 and passkey support."),
        ("Project Beta", "Completed", "Bob Wang", "February 28, 2026",
         "Migrated the legacy monolith to microservices architecture. Successfully deployed to production."),
        ("Project Gamma", "Active", "Carol Li", "April 15, 2026",
         "Developing a real-time analytics dashboard for internal metrics and KPI tracking."),
        ("Project Delta", "On Hold", "David Zhang", "May 1, 2026",
         "Mobile application redesign. Paused pending stakeholder alignment on design direction."),
        ("Project Epsilon", "Planning", "Eva Liu", "June 1, 2026",
         "Infrastructure cost optimization initiative. Currently in requirements gathering phase."),
    ]

    blocks = [
        "Engineering Team Projects Overview",
        "This page tracks all current engineering projects, their status, leads, and deadlines.",
        "",
    ]

    for name, status, lead, deadline, description in projects:
        blocks.append(f"{name}")
        blocks.append(f"Status: {status}")
        blocks.append(f"Lead: {lead}")
        blocks.append(f"Deadline: {deadline}")
        blocks.append(f"Description: {description}")
        blocks.append("")

    for i, text in enumerate(blocks):
        block_data = json.dumps({
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text},
                    "plain_text": text,
                }
            ]
        })
        cur.execute(
            """INSERT INTO notion.blocks (parent_type, parent_id, type, block_data, position)
               VALUES ('page_id', %s, 'paragraph', %s::jsonb, %s)""",
            (page_id, block_data, i),
        )

    print(f"[preprocess] Injected Notion page with {len(blocks)} blocks for 5 projects.")


def inject_form_and_responses(cur):
    """Create the satisfaction survey form and inject 8 responses."""
    print("[preprocess] Injecting Google Form data...")

    form_id = "form-team-satisfaction-001"
    q_name = "q-resp-name-001"
    q_leadership = "q-leadership-001"
    q_workload = "q-workload-001"
    q_communication = "q-communication-001"
    q_growth = "q-growth-001"

    cur.execute(
        """INSERT INTO gform.forms (id, title, document_title, description)
           VALUES (%s, %s, %s, %s)""",
        (
            form_id,
            "Team Satisfaction Survey",
            "Team Satisfaction Survey",
            "Please rate the following dimensions on a scale of 1 to 5.",
        ),
    )

    rating_options = json.dumps({
        "type": "RADIO",
        "options": [
            {"value": "1"}, {"value": "2"}, {"value": "3"},
            {"value": "4"}, {"value": "5"},
        ],
    })

    questions = [
        (q_name, form_id, "Your Name", "textQuestion", True, "{}", 0),
        (q_leadership, form_id, "Leadership (1-5)", "choiceQuestion", True, rating_options, 1),
        (q_workload, form_id, "Workload (1-5)", "choiceQuestion", True, rating_options, 2),
        (q_communication, form_id, "Communication (1-5)", "choiceQuestion", True, rating_options, 3),
        (q_growth, form_id, "Growth (1-5)", "choiceQuestion", True, rating_options, 4),
    ]

    for q in questions:
        cur.execute(
            """INSERT INTO gform.questions
               (id, form_id, title, question_type, required, config, position)
               VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)""",
            q,
        )

    # 10 survey responses
    # Alice: 4,3,5,4 | Bob: 3,4,3,3 | Carol: 5,2,4,5 | David: 3,3,3,2
    # Eva: 4,4,4,4 | Frank: 2,5,3,3 | Grace: 4,3,4,4 | Henry: 3,4,3,3
    # Irene: 4,3,4,4 | Jack: 3,4,3,3
    # Averages: Leadership=3.5, Workload=3.5, Communication=3.6, Growth=3.5
    responses = [
        ("Alice",  "4", "3", "5", "4"),
        ("Bob",    "3", "4", "3", "3"),
        ("Carol",  "5", "2", "4", "5"),
        ("David",  "3", "3", "3", "2"),
        ("Eva",    "4", "4", "4", "4"),
        ("Frank",  "2", "5", "3", "3"),
        ("Grace",  "4", "3", "4", "4"),
        ("Henry",  "3", "4", "3", "3"),
        ("Irene",  "4", "3", "4", "4"),
        ("Jack",   "3", "4", "3", "3"),
    ]

    for name, leadership, workload, communication, growth in responses:
        answers = json.dumps({
            q_name: name,
            q_leadership: leadership,
            q_workload: workload,
            q_communication: communication,
            q_growth: growth,
        })
        email = f"{name.lower()}@company.com"
        cur.execute(
            """INSERT INTO gform.responses (form_id, respondent_email, answers)
               VALUES (%s, %s, %s::jsonb)""",
            (form_id, email, answers),
        )

    print(f"[preprocess] Injected form with {len(questions)} questions and {len(responses)} responses.")


def ensure_email_folder(cur):
    """Ensure INBOX folder exists."""
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO email.folders (name) VALUES ('INBOX') RETURNING id")


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
        inject_form_and_responses(cur)
        ensure_email_folder(cur)
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
