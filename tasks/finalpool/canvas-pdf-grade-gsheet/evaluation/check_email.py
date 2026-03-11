"""
Check that the agent sent grade report emails to course instructors.
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

# Courses with teachers (BBB-2014B has no teacher, so no email expected)
EXPECTED_EMAILS = [
    {
        "course_code": "CCC-2014B",
        "instructor_email": "caleb.miller@openuniversity.ac.uk",
        "class_average": "62.77",
        "letter_grade": "D",
    },
    {
        "course_code": "DDD-2014B",
        "instructor_email": "evan.miller@openuniversity.ac.uk",
        "class_average": "66.47",
        "letter_grade": "D",
    },
    {
        "course_code": "EEE-2014B",
        "instructor_email": "emma.wright@openuniversity.ac.uk",
        "class_average": "78.80",
        "letter_grade": "C",
    },
    {
        "course_code": "FFF-2014B",
        "instructor_email": "caleb.morgan@openuniversity.ac.uk",
        "class_average": "74.67",
        "letter_grade": "C",
    },
    {
        "course_code": "GGG-2014B",
        "instructor_email": "lily.carter@openuniversity.ac.uk",
        "class_average": "77.38",
        "letter_grade": "C",
    },
]


def parse_to_addrs(to_addr):
    """Parse to_addr field (could be JSON array or string)."""
    if isinstance(to_addr, list):
        return [str(r).lower().strip() for r in to_addr]
    if isinstance(to_addr, str):
        try:
            parsed = json.loads(to_addr)
            if isinstance(parsed, list):
                return [str(r).lower().strip() for r in parsed]
        except (json.JSONDecodeError, TypeError):
            pass
        return [to_addr.lower().strip()]
    return []


def check_email():
    """
    Verify that grade report emails were sent to the correct instructors.
    Returns (passed_count, failed_count, error_details).
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
    """)
    all_emails = cur.fetchall()
    cur.close()
    conn.close()

    print(f"  [check_email] Found {len(all_emails)} total emails.")

    passed = 0
    failed = 0
    errors = []

    for expected in EXPECTED_EMAILS:
        code = expected["course_code"]
        target_email = expected["instructor_email"]
        avg = expected["class_average"]
        grade = expected["letter_grade"]

        # Find email for this course
        found = False
        for subject, from_addr, to_addr, body_text in all_emails:
            subject_str = str(subject or "").lower()
            if code.lower() not in subject_str:
                continue

            # Check subject format
            if "end-of-semester grade report" not in subject_str:
                continue

            found = True

            # Check recipient
            recipients = parse_to_addrs(to_addr)
            recipient_ok = any(target_email in r for r in recipients)
            if not recipient_ok:
                errors.append(
                    f"Email for {code}: expected recipient {target_email}, "
                    f"got {recipients}"
                )

            # Check body contains key information
            body_lower = str(body_text or "").lower()
            body_ok = True

            if avg.replace(".", "") not in body_lower.replace(".", ""):
                # Try numeric match with some tolerance
                try:
                    # Just check the avg value appears somewhere
                    if str(avg) not in str(body_text or ""):
                        body_ok = False
                        errors.append(f"Email for {code}: body missing average {avg}")
                except Exception:
                    pass

            if grade.lower() not in body_lower:
                body_ok = False
                errors.append(f"Email for {code}: body missing letter grade {grade}")

            if recipient_ok and body_ok:
                passed += 1
            else:
                failed += 1
            break

        if not found:
            failed += 1
            errors.append(f"No email found for course {code}")

    return passed, failed, errors
