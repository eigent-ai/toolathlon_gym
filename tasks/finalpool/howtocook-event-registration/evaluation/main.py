"""
Evaluation script for howtocook-event-registration task.

Checks via psycopg2:
1. Google Form exists with "cooking" or "lunch" in title, has at least 4 questions
2. Calendar event exists with "cooking" or "lunch" in summary, dated 2026-03-20
3. Notion page exists with "cooking" or "event" or "planning" in properties
4. At least 1 email sent with "lunch" or "cooking" in subject, mentioning March 20
"""

import os
import argparse
import json
import sys

import psycopg2

def num_close(a, b, rel_tol=0.15, abs_tol=0.5):
    return abs(float(a) - float(b)) <= max(abs_tol, abs(float(b)) * rel_tol)


DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        detail_str = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{detail_str}")


def check_google_form():
    """Check that a Google Form was created with the expected structure."""
    print("\n=== Checking Google Form ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Find forms with cooking or lunch in the title
    cur.execute("""
        SELECT id, title
        FROM gform.forms
        WHERE LOWER(title) LIKE '%%cooking%%'
           OR LOWER(title) LIKE '%%lunch%%'
    """)
    forms = cur.fetchall()

    check("Google Form with 'cooking' or 'lunch' in title exists",
          len(forms) > 0,
          "No matching forms found")

    if not forms:
        cur.close()
        conn.close()
        return

    form_id = forms[0][0]
    form_title = forms[0][1]
    print(f"  Found form: '{form_title}' (id={form_id})")

    # Check number of questions
    cur.execute("""
        SELECT id, title, question_type, required
        FROM gform.questions
        WHERE form_id = %s
        ORDER BY position
    """, (form_id,))
    questions = cur.fetchall()

    check("Form has at least 4 questions",
          len(questions) >= 4,
          f"Found {len(questions)} questions, expected at least 4")

    check("Form has 5 questions",
          len(questions) >= 5,
          f"Found {len(questions)} questions, expected 5")

    # Check question content by title keywords
    q_titles_lower = [q[1].lower() for q in questions]

    check("Has a 'name' question",
          any("name" in t for t in q_titles_lower),
          f"Question titles: {[q[1] for q in questions]}")

    check("Has an 'email' question",
          any("email" in t for t in q_titles_lower),
          f"Question titles: {[q[1] for q in questions]}")

    check("Has a 'department' question",
          any("department" in t for t in q_titles_lower),
          f"Question titles: {[q[1] for q in questions]}")

    check("Has a 'dietary' or 'restriction' question",
          any("diet" in t or "restriction" in t for t in q_titles_lower),
          f"Question titles: {[q[1] for q in questions]}")

    check("Has a 'dish' or 'excited' question",
          any("dish" in t or "excited" in t for t in q_titles_lower),
          f"Question titles: {[q[1] for q in questions]}")

    # Check required fields
    required_questions = [q for q in questions if q[3] is True]
    check("At least 3 required questions",
          len(required_questions) >= 3,
          f"Found {len(required_questions)} required questions")

    cur.close()
    conn.close()


def check_calendar():
    """Check Google Calendar event."""
    print("\n=== Checking Google Calendar ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT summary, description, start_datetime, end_datetime, location
        FROM gcal.events
        WHERE LOWER(summary) LIKE '%%cooking%%'
           OR LOWER(summary) LIKE '%%lunch%%'
    """)
    events = cur.fetchall()

    check("Calendar event with 'cooking' or 'lunch' exists",
          len(events) > 0,
          "No matching calendar events found")

    if not events:
        cur.close()
        conn.close()
        return

    event = events[0]
    summary, description, start_dt, end_dt, location = event
    print(f"  Found event: '{summary}'")

    # Check date is 2026-03-20
    if start_dt:
        date_str = start_dt.strftime("%Y-%m-%d")
        check("Event date is 2026-03-20",
              date_str == "2026-03-20",
              f"Got {date_str}")

        # Check approximate start time (12:00 PM, with wide TZ tolerance)
        hour = start_dt.hour
        check("Event starts around noon (8-18 range for TZ tolerance)",
              8 <= hour <= 18,
              f"Got hour {hour}")
    else:
        check("Event has a start datetime", False, "start_datetime is null")

    # Check duration (~1.5 hours)
    if start_dt and end_dt:
        duration_hours = (end_dt - start_dt).total_seconds() / 3600
        check("Event duration is ~1.5 hours",
              1.0 <= duration_hours <= 2.0,
              f"Got {duration_hours:.1f} hours")

    # Check description mentions dishes
    if description:
        check("Event description is not empty",
              len(description.strip()) > 10,
              f"Description length: {len(description.strip())}")
    else:
        check("Event description exists", False, "description is null")

    # Check location
    if location:
        check("Event location mentions 'kitchen' or is set",
              "kitchen" in location.lower() or len(location.strip()) > 0,
              f"Location: '{location}'")
    else:
        # Location might be in description
        desc_lower = (description or "").lower()
        check("Location info present (in description or location field)",
              "kitchen" in desc_lower or "company" in desc_lower,
              "No location info found")

    cur.close()
    conn.close()


def check_notion():
    """Check Notion page for cooking event planning."""
    print("\n=== Checking Notion ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, properties
        FROM notion.pages
        WHERE LOWER(properties::text) LIKE '%%cooking%%'
           OR LOWER(properties::text) LIKE '%%event%%'
           OR LOWER(properties::text) LIKE '%%planning%%'
        LIMIT 5
    """)
    pages = cur.fetchall()

    check("Notion page with 'cooking', 'event', or 'planning' exists",
          len(pages) > 0,
          "No matching Notion pages found")

    if not pages:
        # Broader search
        cur.execute("SELECT id, properties FROM notion.pages")
        all_pages = cur.fetchall()
        check("Any Notion page exists",
              len(all_pages) > 0,
              f"Found {len(all_pages)} total pages")
        cur.close()
        conn.close()
        return

    page_id = pages[0][0]
    props = pages[0][1]
    print(f"  Found page id: {page_id}")

    # Check for content blocks
    cur.execute("""
        SELECT COUNT(*)
        FROM notion.blocks
        WHERE parent_id = %s
    """, (page_id,))
    block_count = cur.fetchone()[0]

    # Also check all blocks if none found for this specific page
    if block_count == 0:
        cur.execute("SELECT COUNT(*) FROM notion.blocks")
        block_count = cur.fetchone()[0]

    check("Notion page has content blocks",
          block_count >= 2,
          f"Found {block_count} blocks, expected at least 2")

    # Check block content for cooking-related terms
    cur.execute("""
        SELECT block_data::text
        FROM notion.blocks
    """)
    blocks = cur.fetchall()

    all_text = ""
    for b in blocks:
        if b[0]:
            all_text += str(b[0]).lower() + " "

    # Also include page properties
    if props:
        all_text += str(props).lower()

    has_logistics = ("march" in all_text or "2026" in all_text or
                     "12:00" in all_text or "kitchen" in all_text)
    check("Notion page mentions event logistics (date/time/location)",
          has_logistics,
          "No date, time, or location info found in page content")

    has_recipe_content = ("ingredient" in all_text or "step" in all_text or
                          "recipe" in all_text or "cook" in all_text or
                          "dish" in all_text)
    check("Notion page mentions recipe content (ingredients/steps/dish)",
          has_recipe_content,
          "No recipe-related content found")

    cur.close()
    conn.close()


def check_emails():
    """Check that announcement email was sent."""
    print("\n=== Checking Emails ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
        WHERE LOWER(subject) LIKE '%%lunch%%'
           OR LOWER(subject) LIKE '%%cooking%%'
    """)
    emails = cur.fetchall()

    check("At least 1 email with 'lunch' or 'cooking' in subject",
          len(emails) >= 1,
          f"Found {len(emails)} matching emails")

    if not emails:
        # Check if any emails exist at all
        cur.execute("SELECT COUNT(*) FROM email.messages")
        total = cur.fetchone()[0]
        check("Any emails sent", total > 0, f"Found {total} total emails")
        cur.close()
        conn.close()
        return

    email_row = emails[0]
    subject, from_addr, to_addr, body_text = email_row
    print(f"  Found email with subject: '{subject}'")

    # Check subject mentions March 20
    subject_lower = (subject or "").lower()
    check("Email subject mentions 'march 20'",
          "march 20" in subject_lower or "3/20" in subject_lower or
          "03-20" in subject_lower or "march20" in subject_lower,
          f"Subject: '{subject}'")

    # Check body mentions March 20
    body_lower = (body_text or "").lower()
    has_date = ("march 20" in body_lower or "2026-03-20" in body_lower or
                "3/20" in body_lower or "march 20, 2026" in body_lower)
    check("Email body mentions March 20",
          has_date,
          "Date not found in email body")

    # Check body mentions time
    has_time = ("12:00" in body_lower or "12 pm" in body_lower or
                "1:30" in body_lower or "1:30 pm" in body_lower or
                "13:30" in body_lower)
    check("Email body mentions event time",
          has_time,
          "Time not found in email body")

    # Check body mentions location
    has_location = "kitchen" in body_lower or "company kitchen" in body_lower
    check("Email body mentions Company Kitchen",
          has_location,
          "Kitchen/location not found in email body")

    # Check from address
    if from_addr:
        from_str = str(from_addr).lower()
        check("Email sent from hr@company.com",
              "hr" in from_str,
              f"From: '{from_addr}'")

    # Check to address
    if to_addr:
        to_str = str(to_addr).lower()
        check("Email sent to all-staff@company.com",
              "all-staff" in to_str or "all_staff" in to_str or "staff" in to_str,
              f"To: '{to_addr}'")

    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    check_google_form()
    check_calendar()
    check_notion()
    check_emails()

    total = PASS_COUNT + FAIL_COUNT
    pass_rate = PASS_COUNT / total if total > 0 else 0

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    print(f"  Pass Rate: {pass_rate:.1%}")
    print(f"  Overall: {'PASS' if pass_rate >= 0.8 else 'FAIL'}")

    if args.res_log_file:
        result = {
            "passed": PASS_COUNT,
            "failed": FAIL_COUNT,
            "pass_rate": round(pass_rate, 3),
            "success": pass_rate >= 0.8,
        }
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    sys.exit(0 if pass_rate >= 0.8 else 1)


if __name__ == "__main__":
    main()
