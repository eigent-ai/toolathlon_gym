"""
Evaluation for howtocook-weekly-gsheet-gcal task.

Checks:
1. GSheet "Weekly Meal Plan" exists in gsheet.spreadsheets
2. GSheet has 21 data rows (7 days x 3 meals)
3. GCal has at least 7 dinner prep events in April 2026
4. Email sent to meal_planning@service.com
"""
import json
import os
import sys
from argparse import ArgumentParser

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PASS_COUNT = 0
FAIL_COUNT = 0


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def check_gsheet():
    print("\n=== Check 1: Google Sheet Weekly Meal Plan ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title FROM gsheet.spreadsheets
        WHERE title ILIKE '%meal plan%' OR title ILIKE '%weekly%'
        ORDER BY created_at DESC
        LIMIT 1
    """)
    spreadsheet = cur.fetchone()

    if not spreadsheet:
        # Try any spreadsheet
        cur.execute("SELECT id, title FROM gsheet.spreadsheets ORDER BY created_at DESC LIMIT 1")
        spreadsheet = cur.fetchone()

    record("Weekly Meal Plan spreadsheet exists", spreadsheet is not None,
           "No spreadsheet found with 'meal plan' or 'weekly' in title")

    if spreadsheet:
        spreadsheet_id, title = spreadsheet
        record("Spreadsheet title contains 'meal' or 'weekly'",
               "meal" in title.lower() or "weekly" in title.lower(),
               f"Title: {title}")

        # Count data rows (non-header rows with data)
        cur.execute("""
            SELECT COUNT(DISTINCT row_index) FROM gsheet.cells
            WHERE spreadsheet_id = %s AND row_index > 0
            AND value IS NOT NULL AND value != ''
        """, (spreadsheet_id,))
        data_row_count = cur.fetchone()[0]
        record("GSheet has at least 21 data rows", data_row_count >= 21,
               f"Found {data_row_count} non-header rows with data")

        # Check for meal type values
        cur.execute("""
            SELECT DISTINCT value FROM gsheet.cells
            WHERE spreadsheet_id = %s AND row_index > 0
            AND (LOWER(value) IN ('breakfast', 'lunch', 'dinner'))
        """, (spreadsheet_id,))
        meal_types = [r[0] for r in cur.fetchall()]
        record("GSheet contains Breakfast, Lunch, Dinner meal types",
               len(meal_types) >= 2,
               f"Found meal types: {meal_types}")

    cur.close()
    conn.close()


def check_gcal():
    print("\n=== Check 2: Google Calendar Dinner Prep Events ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT summary, start_datetime, end_datetime
        FROM gcal.events
        WHERE start_datetime >= '2026-04-07' AND start_datetime <= '2026-04-13 23:59:59'
        AND (summary ILIKE '%dinner%' OR summary ILIKE '%dinner prep%')
        ORDER BY start_datetime
    """)
    events = cur.fetchall()

    # Also check for any events in April 2026 if dinner-specific not found
    if not events:
        cur.execute("""
            SELECT summary, start_datetime, end_datetime
            FROM gcal.events
            WHERE start_datetime >= '2026-04-07' AND start_datetime <= '2026-04-13 23:59:59'
            ORDER BY start_datetime
        """)
        events = cur.fetchall()

    cur.close()
    conn.close()

    record("At least 7 dinner prep events Apr 7-13 2026", len(events) >= 7,
           f"Found {len(events)} events in Apr 7-13")

    if events:
        # Check time (18:00-19:00)
        summary, start_dt, end_dt = events[0]
        if start_dt:
            hour = start_dt.hour
            record("Events start at 18:00", hour == 18,
                   f"First event starts at {start_dt}")

        # Check different days
        dates = set(e[1].date() for e in events if e[1])
        record("Events on 7 distinct days", len(dates) >= 7,
               f"Distinct dates: {sorted(dates)}")


def check_email():
    print("\n=== Check 3: Email to meal_planning@service.com ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
    """)
    messages = cur.fetchall()
    cur.close()
    conn.close()

    matching = None
    for subject, from_addr, to_addr, body_text in messages:
        to_str = ""
        if isinstance(to_addr, list):
            to_str = " ".join(str(r).lower() for r in to_addr)
        elif isinstance(to_addr, str):
            try:
                parsed = json.loads(to_addr)
                to_str = " ".join(str(r).lower() for r in parsed) if isinstance(parsed, list) else str(to_addr).lower()
            except Exception:
                to_str = str(to_addr).lower()
        if "meal_planning@service.com" in to_str:
            matching = (subject, from_addr, to_addr, body_text)
            break

    record("Email sent to meal_planning@service.com", matching is not None,
           f"Messages found: {len(messages)}")

    if matching:
        subject, _, _, body_text = matching
        all_text = ((subject or "") + " " + (body_text or "")).lower()
        has_meal_content = (
            "meal plan" in all_text or "weekly" in all_text or
            "breakfast" in all_text or "dinner" in all_text
        )
        record("Email mentions meal plan content", has_meal_content,
               f"Subject: {subject}")


def main():
    parser = ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    check_gsheet()
    check_gcal()
    check_email()

    total = PASS_COUNT + FAIL_COUNT
    if total == 0:
        print("\nFAIL: No checks were performed.")
        sys.exit(1)

    accuracy = PASS_COUNT / total * 100
    print(f"\nOverall: {PASS_COUNT}/{total} checks passed ({accuracy:.1f}%)")

    result = {
        "total_passed": PASS_COUNT,
        "total_checks": total,
        "accuracy": accuracy,
    }

    if args.res_log_file:
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    if accuracy >= 70:
        print("PASS")
        sys.exit(0)
    else:
        print("FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
