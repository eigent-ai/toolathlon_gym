"""
Preprocess script for gcal-canvas-office-hours task.

Canvas is read-only, so no changes there.
This script:
1. Queries Canvas DB for real student names from "Applied Analytics & Algorithms"
2. Clears writable schemas (email, gcal, gform)
3. Injects a Google Form "Office Hours Booking" with 5 questions and 6 responses
"""

import os
import argparse
import json
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

# Fallback student data in case Canvas query fails or returns too few
FALLBACK_STUDENTS = [
    ("Emily Chen", "emily.chen@university.edu"),
    ("Marcus Johnson", "marcus.johnson@university.edu"),
    ("Sophia Patel", "sophia.patel@university.edu"),
    ("Liam O'Brien", "liam.obrien@university.edu"),
    ("Ava Williams", "ava.williams@university.edu"),
    ("Noah Garcia", "noah.garcia@university.edu"),
]

# Office hour booking data: (date, time_slot, topic) for each of the 6 students
# Using varied dates (March 9-13) and time slots (9:00 AM, 10:00 AM, 11:00 AM, 2:00 PM)
BOOKING_DATA = [
    ("March 9, 2026", "9:00 AM", "Homework 3"),
    ("March 9, 2026", "10:00 AM", "Midterm Review"),
    ("March 10, 2026", "11:00 AM", "Project Help"),
    ("March 11, 2026", "2:00 PM", "Algorithm Analysis"),
    ("March 12, 2026", "10:00 AM", "Graph Algorithms"),
    ("March 13, 2026", "2:00 PM", "Dynamic Programming"),
]


def get_canvas_students(cur):
    """Try to get real student names from Canvas DB for an Analytics/Algorithms course."""
    try:
        cur.execute("""
            SELECT DISTINCT u.name, u.id
            FROM canvas.users u
            JOIN canvas.enrollments e ON u.id = e.user_id
            JOIN canvas.courses c ON e.course_id = c.id
            WHERE c.name ILIKE '%%Analytics%%Algorithm%%'
              AND e.type = 'StudentEnrollment'
            ORDER BY u.name
            LIMIT 10
        """)
        rows = cur.fetchall()
        if len(rows) >= 6:
            # Build email from name: lowercase, replace spaces with dots
            students = []
            for name, uid in rows[:6]:
                email_name = name.strip().lower().replace(" ", ".").replace("'", "")
                students.append((name.strip(), f"{email_name}@university.edu"))
            return students
    except Exception as e:
        print(f"[preprocess] Canvas query failed: {e}")
    return None


def clear_writable_schemas(cur):
    """Clear all writable schemas in FK-safe order."""
    print("[preprocess] Clearing writable schemas...")
    # Email
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    # Google Forms
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    # Google Calendar
    cur.execute("DELETE FROM gcal.events")
    print("[preprocess] Writable schemas cleared.")


def inject_form_data(cur, students):
    """Inject the Office Hours Booking form with 5 questions and 6 responses."""
    print("[preprocess] Injecting Google Form data...")

    form_id = "form-office-hours-001"
    q_name_id = "q-oh-name"
    q_email_id = "q-oh-email"
    q_date_id = "q-oh-date"
    q_time_id = "q-oh-time"
    q_topic_id = "q-oh-topic"

    # Create form
    cur.execute(
        """INSERT INTO gform.forms (id, title, document_title, description)
           VALUES (%s, %s, %s, %s)""",
        (form_id, "Office Hours Booking", "Office Hours Booking",
         "Book your preferred office hour slot for the week of March 9-13, 2026."),
    )

    # Create questions
    questions = [
        (q_name_id, form_id, "Student Name", "textQuestion", True, "{}", 0),
        (q_email_id, form_id, "Student Email", "textQuestion", True, "{}", 1),
        (
            q_date_id, form_id, "Preferred Date", "choiceQuestion", True,
            json.dumps({
                "type": "RADIO",
                "options": [
                    {"value": "March 9, 2026"},
                    {"value": "March 10, 2026"},
                    {"value": "March 11, 2026"},
                    {"value": "March 12, 2026"},
                    {"value": "March 13, 2026"},
                ],
            }),
            2,
        ),
        (
            q_time_id, form_id, "Preferred Time Slot", "choiceQuestion", True,
            json.dumps({
                "type": "RADIO",
                "options": [
                    {"value": "9:00 AM"},
                    {"value": "10:00 AM"},
                    {"value": "11:00 AM"},
                    {"value": "2:00 PM"},
                ],
            }),
            3,
        ),
        (q_topic_id, form_id, "Topic", "textQuestion", True, "{}", 4),
    ]

    for q in questions:
        cur.execute(
            """INSERT INTO gform.questions
               (id, form_id, title, question_type, required, config, position)
               VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s)""",
            q,
        )

    # Insert 6 responses
    for i, (student_name, student_email) in enumerate(students):
        date, time_slot, topic = BOOKING_DATA[i]
        answers = json.dumps({
            q_name_id: student_name,
            q_email_id: student_email,
            q_date_id: date,
            q_time_id: time_slot,
            q_topic_id: topic,
        })
        cur.execute(
            """INSERT INTO gform.responses (form_id, respondent_email, answers)
               VALUES (%s, %s, %s::jsonb)""",
            (form_id, student_email, answers),
        )

    print(f"[preprocess] Injected form with {len(questions)} questions and {len(students)} responses.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Step 1: Try to get real Canvas students
        print("[preprocess] Querying Canvas for student data...")
        students = get_canvas_students(cur)
        if students:
            print(f"[preprocess] Found {len(students)} students from Canvas.")
        else:
            print("[preprocess] Using fallback student data.")
            students = FALLBACK_STUDENTS

        # Step 2: Clear writable schemas
        clear_writable_schemas(cur)

        # Step 3: Inject form data
        inject_form_data(cur, students)

        conn.commit()
        print("[preprocess] Database operations committed.")

        # Print summary for debugging
        print("\n[preprocess] Students used:")
        for name, email in students:
            print(f"  - {name} ({email})")
        print("\n[preprocess] Bookings injected:")
        for i, (name, email) in enumerate(students):
            date, time_slot, topic = BOOKING_DATA[i]
            print(f"  - {name}: {date} {time_slot} - {topic}")

    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    main()
