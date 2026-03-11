"""
Preprocess script for gform-canvas-peer-review task.

Canvas is read-only, so no changes there.
This script:
1. Clears writable schemas (gform, gsheet, notion)
2. Creates a Google Form "Group Project Peer Review" with 6 questions
3. Injects 20 peer review responses for 6 students
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


def clear_writable_schemas(cur):
    """Clear all writable schemas in FK-safe order."""
    print("[preprocess] Clearing writable schemas...")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.permissions")
    cur.execute("DELETE FROM gsheet.sheets")
    cur.execute("DELETE FROM gsheet.spreadsheets")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    cur.execute("DELETE FROM notion.users")
    print("[preprocess] All writable schemas cleared.")


def inject_form_and_responses(cur):
    """Create the peer review form and inject 20 responses."""
    print("[preprocess] Injecting peer review form and responses...")

    form_id = "form-peer-review-001"
    q_reviewer = "q-reviewer-001"
    q_reviewee = "q-reviewee-001"
    q_contribution = "q-contribution-001"
    q_communication = "q-communication-001"
    q_quality = "q-quality-001"
    q_comments = "q-comments-001"

    # Create form
    cur.execute(
        """INSERT INTO gform.forms (id, title, document_title, description)
           VALUES (%s, %s, %s, %s)""",
        (
            form_id,
            "Group Project Peer Review",
            "Group Project Peer Review",
            "Please evaluate your group members on their contribution, communication, and quality of work for the Biochemistry & Bioinformatics group project.",
        ),
    )

    # Create questions
    questions = [
        (q_reviewer, form_id, "Your Name", "textQuestion", True, "{}", 0),
        (q_reviewee, form_id, "Person Being Reviewed", "textQuestion", True, "{}", 1),
        (
            q_contribution,
            form_id,
            "Contribution Score (1-5)",
            "choiceQuestion",
            True,
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
            2,
        ),
        (
            q_communication,
            form_id,
            "Communication Score (1-5)",
            "choiceQuestion",
            True,
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
            3,
        ),
        (
            q_quality,
            form_id,
            "Quality of Work (1-5)",
            "choiceQuestion",
            True,
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
        (q_comments, form_id, "Comments", "textQuestion", False, "{}", 5),
    ]

    for q in questions:
        cur.execute(
            """INSERT INTO gform.questions
               (id, form_id, title, question_type, required, config, position)
               VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)""",
            q,
        )

    # 20 peer review responses for 6 students
    # Students: Alice Wong, Bob Martinez, Carol Zhang, David Kim, Eva Patel, Frank Liu
    # Each student reviews 3-4 others (not themselves)
    # Alice Wong: high performer (~4.5 avg received)
    # Frank Liu: low performer (~2.3 avg received, should be flagged)
    # Others: moderate (3.0 - 4.2 range)
    responses = [
        # Alice Wong reviews: Bob, Carol, David
        ("Alice Wong", "Bob Martinez", "4", "3", "4", "Bob was solid on the lab work."),
        ("Alice Wong", "Carol Zhang", "4", "4", "5", "Carol did an excellent job on the report."),
        ("Alice Wong", "David Kim", "3", "4", "3", "David could have contributed more to coding."),

        # Bob Martinez reviews: Alice, Eva, Frank
        ("Bob Martinez", "Alice Wong", "5", "5", "4", "Alice led the group effectively."),
        ("Bob Martinez", "Eva Patel", "4", "3", "4", "Eva's data analysis was thorough."),
        ("Bob Martinez", "Frank Liu", "2", "2", "3", "Frank missed several meetings."),

        # Carol Zhang reviews: Alice, David, Frank
        ("Carol Zhang", "Alice Wong", "5", "4", "5", "Alice was the driving force of our project."),
        ("Carol Zhang", "David Kim", "4", "3", "4", "David did decent work on the presentation."),
        ("Carol Zhang", "Frank Liu", "2", "3", "2", "Frank submitted his part late and it needed revisions."),

        # David Kim reviews: Alice, Bob, Frank, Eva
        ("David Kim", "Alice Wong", "4", "5", "5", "Excellent leadership from Alice."),
        ("David Kim", "Bob Martinez", "3", "4", "3", "Bob was reliable but not very proactive."),
        ("David Kim", "Frank Liu", "3", "2", "2", "Frank's work quality was below expectations."),
        ("David Kim", "Eva Patel", "3", "4", "3", "Eva communicated well but could improve output."),

        # Eva Patel reviews: Alice, Bob, Carol, Frank
        ("Eva Patel", "Alice Wong", "5", "4", "4", "Alice always kept us on track."),
        ("Eva Patel", "Bob Martinez", "4", "4", "4", "Bob was a dependable team member."),
        ("Eva Patel", "Carol Zhang", "3", "4", "4", "Carol's writing was strong."),
        ("Eva Patel", "Frank Liu", "2", "2", "2", "Frank did not pull his weight."),

        # Frank Liu reviews: Alice, Carol, David
        ("Frank Liu", "Alice Wong", "4", "5", "5", "Alice was great."),
        ("Frank Liu", "Carol Zhang", "4", "3", "4", "Carol was helpful with the writeup."),
        ("Frank Liu", "David Kim", "3", "3", "4", "David did okay on his parts."),
    ]

    for reviewer, reviewee, contrib, comm, quality, comments in responses:
        answers = json.dumps({
            q_reviewer: reviewer,
            q_reviewee: reviewee,
            q_contribution: contrib,
            q_communication: comm,
            q_quality: quality,
            q_comments: comments,
        })
        # Use reviewer email-style as respondent_email
        email = reviewer.lower().replace(" ", ".") + "@university.edu"
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
        clear_writable_schemas(cur)
        inject_form_and_responses(cur)
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
