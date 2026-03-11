"""
Check that the agent sent the summary email correctly.
"""

import os
import json
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

# Course codes that should be mentioned in the email body
EXPECTED_COURSE_CODES = [
    "AAA-2013J", "BBB-2013J", "DDD-2013J",
    "EEE-2013J", "FFF-2013J", "GGG-2013J",
]


def check_email():
    """
    Verify the summary email was sent with correct content.
    Returns (pass: bool, error_msg: str or None).
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Check all messages for the summary email
    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
    """)
    all_emails = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[check_email] Found {len(all_emails)} total emails.")

    # Find the summary email
    summary_email = None
    for subject, from_addr, to_addr, body_text in all_emails:
        subject_lower = (subject or "").lower()
        if "fall 2013" in subject_lower and "final exam" in subject_lower:
            summary_email = (subject, from_addr, to_addr, body_text)
            break

    if summary_email is None:
        return False, (
            "Could not find summary email with 'Fall 2013' and "
            "'Final Exam' in the subject"
        )

    subject, from_addr, to_addr, body_text = summary_email
    print(f"[check_email] Found summary email: {subject}")

    differences = []

    # Check subject
    if "fall 2013 final exam schedule summary" not in subject.lower():
        differences.append(
            f"Subject mismatch: expected 'Fall 2013 Final Exam Schedule Summary', "
            f"got '{subject}'"
        )

    # Check recipient
    to_str = ""
    if isinstance(to_addr, list):
        to_str = " ".join(str(r).lower() for r in to_addr)
    elif isinstance(to_addr, str):
        try:
            parsed = json.loads(to_addr)
            if isinstance(parsed, list):
                to_str = " ".join(str(r).lower() for r in parsed)
            else:
                to_str = str(to_addr).lower()
        except (json.JSONDecodeError, TypeError):
            to_str = str(to_addr).lower()

    if "dept-admin@openuniversity.ac.uk" not in to_str:
        differences.append(
            f"Recipient mismatch: expected dept-admin@openuniversity.ac.uk, "
            f"got '{to_addr}'"
        )

    # Check body mentions all course codes
    body_lower = (body_text or "").lower()
    for code in EXPECTED_COURSE_CODES:
        if code.lower() not in body_lower:
            differences.append(f"Email body missing course code: {code}")

    # Check body mentions TBD (2 courses have no due date)
    if "tbd" not in body_lower:
        differences.append("Email body does not mention 'TBD' for exams without dates")

    if differences:
        return False, (
            f"Email issues: {'; '.join(differences[:5])}"
        )

    print("[check_email] Summary email verified successfully.")
    return True, None
