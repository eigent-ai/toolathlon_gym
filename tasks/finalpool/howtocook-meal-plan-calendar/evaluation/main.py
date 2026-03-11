"""
Evaluation script for howtocook-meal-plan-calendar task.

Checks via psycopg2:
1. Google Sheet: spreadsheet with title containing "lunch" or "menu",
   2 sheets ("Weekly Menu" with 5+ data rows, "Shopping List" with data)
2. Google Calendar: 5 events between March 9-13 2026, each noon-1pm
3. Email: at least 1 sent to team@company.com with subject containing
   "lunch" and "march"

Usage:
    python -m evaluation.main \
        --agent_workspace /path/to/workspace \
        --groundtruth_workspace /path/to/groundtruth \
        --launch_time "2026-03-06 10:00:00"
"""

import os
import argparse
import json
import sys

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


# =========================================================================
# Check 1: Google Sheet
# =========================================================================

def check_gsheet():
    """Verify spreadsheet with weekly menu and shopping list."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Find spreadsheet with title containing "lunch" or "menu"
    cur.execute("SELECT id, title FROM gsheet.spreadsheets")
    spreadsheets = cur.fetchall()
    print(f"[check_gsheet] Found {len(spreadsheets)} spreadsheets.")

    target_ss = None
    for ss_id, title in spreadsheets:
        title_lower = (title or "").lower()
        if "lunch" in title_lower or "menu" in title_lower:
            target_ss = (ss_id, title)
            break

    if not target_ss:
        cur.close()
        conn.close()
        return False, f"No spreadsheet found with 'lunch' or 'menu' in title. Found: {[t for _, t in spreadsheets]}"

    ss_id, ss_title = target_ss
    record("gsheet: spreadsheet found", True)
    print(f"[check_gsheet] Using spreadsheet: {ss_title} ({ss_id})")

    # Check sheets
    cur.execute(
        "SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s ORDER BY index",
        (str(ss_id),)
    )
    sheets = cur.fetchall()
    sheet_titles = [t for _, t in sheets]
    print(f"[check_gsheet] Sheets: {sheet_titles}")

    record("gsheet: has at least 2 sheets", len(sheets) >= 2,
           f"Found {len(sheets)} sheets: {sheet_titles}")

    # Check "Weekly Menu" sheet
    menu_sheet = None
    shopping_sheet = None
    for sheet_id, sheet_title in sheets:
        title_lower = (sheet_title or "").lower()
        if "menu" in title_lower or "weekly" in title_lower:
            menu_sheet = (sheet_id, sheet_title)
        if "shopping" in title_lower or "list" in title_lower or "ingredient" in title_lower:
            shopping_sheet = (sheet_id, sheet_title)

    record("gsheet: 'Weekly Menu' sheet found", menu_sheet is not None,
           f"No sheet with 'menu' or 'weekly' in title. Sheets: {sheet_titles}")
    record("gsheet: 'Shopping List' sheet found", shopping_sheet is not None,
           f"No sheet with 'shopping'/'list'/'ingredient' in title. Sheets: {sheet_titles}")

    # Check Weekly Menu data rows (should have 5 data rows for Mon-Fri)
    if menu_sheet:
        menu_sheet_id = menu_sheet[0]
        cur.execute(
            "SELECT DISTINCT row_index FROM gsheet.cells WHERE sheet_id = %s ORDER BY row_index",
            (menu_sheet_id,)
        )
        rows = [r[0] for r in cur.fetchall()]
        # The first row (min index) is the header; everything else is data
        min_row = min(rows) if rows else 0
        data_rows = [r for r in rows if r > min_row]
        record("gsheet: Weekly Menu has 5 data rows", len(data_rows) >= 5,
               f"Found {len(data_rows)} data rows (row indices: {rows})")

        # Check that menu sheet has content with day names
        cur.execute(
            "SELECT row_index, col_index, value FROM gsheet.cells "
            "WHERE sheet_id = %s AND row_index > %s ORDER BY row_index, col_index",
            (menu_sheet_id, min_row)
        )
        cells = cur.fetchall()
        all_values = " ".join((v or "").lower() for _, _, v in cells)

        days_found = 0
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            if day in all_values:
                days_found += 1
        record("gsheet: Weekly Menu mentions all 5 weekdays", days_found >= 5,
               f"Found {days_found}/5 weekday names in menu data")

    # Check Shopping List has data
    if shopping_sheet:
        shopping_sheet_id = shopping_sheet[0]
        cur.execute(
            "SELECT DISTINCT row_index FROM gsheet.cells WHERE sheet_id = %s ORDER BY row_index",
            (shopping_sheet_id,)
        )
        all_shopping_rows = [r[0] for r in cur.fetchall()]
        if all_shopping_rows:
            min_shop_row = min(all_shopping_rows)
            shopping_data_rows = [r for r in all_shopping_rows if r > min_shop_row]
        else:
            shopping_data_rows = []
        record("gsheet: Shopping List has ingredient rows", len(shopping_data_rows) >= 3,
               f"Found {len(shopping_data_rows)} data rows in Shopping List")

    cur.close()
    conn.close()

    # Overall gsheet pass
    all_ok = (
        target_ss is not None
        and len(sheets) >= 2
        and menu_sheet is not None
        and shopping_sheet is not None
    )
    return all_ok, None if all_ok else "Some gsheet checks failed"


# =========================================================================
# Check 2: Google Calendar
# =========================================================================

def check_gcal():
    """Verify 5 calendar events for March 9-13, 2026 around noon."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT summary, description, start_datetime, end_datetime
        FROM gcal.events
        WHERE start_datetime >= '2026-03-09 00:00:00'
          AND start_datetime < '2026-03-14 00:00:00'
        ORDER BY start_datetime
    """)
    events = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[check_gcal] Found {len(events)} calendar events in March 9-13.")
    for ev in events:
        print(f"  Event: {ev[0]} | {ev[2]} - {ev[3]}")

    record("gcal: at least 5 events in March 9-13", len(events) >= 5,
           f"Found {len(events)} events")

    # Check each weekday has at least one event
    days_covered = set()
    noon_events = 0
    events_with_description = 0

    for summary, description, start_dt, end_dt in events:
        if start_dt:
            day = start_dt.strftime("%Y-%m-%d")
            days_covered.add(day)

            # Check start time is around noon (between 11:00 and 13:00)
            hour = start_dt.hour
            if 11 <= hour <= 13:
                noon_events += 1

        if description and len(description.strip()) > 5:
            events_with_description += 1

    expected_days = {"2026-03-09", "2026-03-10", "2026-03-11", "2026-03-12", "2026-03-13"}
    missing_days = expected_days - days_covered
    record("gcal: events cover all 5 weekdays", len(missing_days) == 0,
           f"Missing days: {missing_days}")

    record("gcal: events start around noon", noon_events >= 5,
           f"Only {noon_events}/5 events start between 11:00-13:00")

    record("gcal: events have descriptions with ingredients",
           events_with_description >= 5,
           f"Only {events_with_description}/5 events have non-trivial descriptions")

    all_ok = (
        len(events) >= 5
        and len(missing_days) == 0
        and noon_events >= 5
        and events_with_description >= 5
    )
    return all_ok, None if all_ok else "Some gcal checks failed"


# =========================================================================
# Check 3: Email
# =========================================================================

def check_email():
    """Verify notification email sent to team@company.com."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
    """)
    all_emails = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[check_email] Found {len(all_emails)} total emails.")

    # Find the notification email
    target_email = None
    for subject, from_addr, to_addr, body_text in all_emails:
        subject_lower = (subject or "").lower()
        if ("lunch" in subject_lower or "menu" in subject_lower) and "march" in subject_lower:
            target_email = (subject, from_addr, to_addr, body_text)
            break

    if not target_email:
        # Fallback: any email to team@company.com
        for subject, from_addr, to_addr, body_text in all_emails:
            to_str = _to_addr_str(to_addr)
            if "team@company.com" in to_str:
                target_email = (subject, from_addr, to_addr, body_text)
                break

    record("email: notification email found", target_email is not None,
           f"No email with 'lunch'/'menu' and 'march' in subject. "
           f"Found subjects: {[s for s, _, _, _ in all_emails]}")

    if not target_email:
        return False, "Notification email not found"

    subject, from_addr, to_addr, body_text = target_email
    print(f"[check_email] Found email: {subject}")

    # Check recipient
    to_str = _to_addr_str(to_addr)
    record("email: sent to team@company.com", "team@company.com" in to_str,
           f"Recipient: {to_addr}")

    # Check subject contains expected text
    subject_lower = (subject or "").lower()
    record("email: subject mentions 'march'", "march" in subject_lower,
           f"Subject: {subject}")

    # Check body mentions weekdays and dishes
    body_lower = (body_text or "").lower()
    days_in_body = 0
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        if day in body_lower:
            days_in_body += 1
    record("email: body mentions weekdays", days_in_body >= 3,
           f"Found {days_in_body}/5 weekday names in body")

    record("email: body has substantial content", len(body_text or "") > 50,
           f"Body length: {len(body_text or '')} chars")

    all_ok = (
        target_email is not None
        and "team@company.com" in to_str
        and days_in_body >= 3
    )
    return all_ok, None if all_ok else "Some email checks failed"


def _to_addr_str(to_addr):
    """Convert to_addr (JSONB or string) to a lowercase search string."""
    if isinstance(to_addr, list):
        return " ".join(str(r).lower() for r in to_addr)
    elif isinstance(to_addr, str):
        try:
            parsed = json.loads(to_addr)
            if isinstance(parsed, list):
                return " ".join(str(r).lower() for r in parsed)
            return str(to_addr).lower()
        except (json.JSONDecodeError, TypeError):
            return str(to_addr).lower()
    return str(to_addr or "").lower()


# =========================================================================
# Main
# =========================================================================

def run_evaluation(agent_workspace, groundtruth_workspace, launch_time, res_log_file):
    """Run all evaluation checks."""

    print("\n=== Checking Google Sheet ===")
    gsheet_pass, gsheet_err = check_gsheet()

    print("\n=== Checking Google Calendar ===")
    gcal_pass, gcal_err = check_gcal()

    print("\n=== Checking Email ===")
    email_pass, email_err = check_email()

    all_passed = gsheet_pass and gcal_pass and email_pass

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    print(f"  Overall: {'PASS' if all_passed else 'FAIL'}")

    if res_log_file:
        result = {
            "passed": PASS_COUNT,
            "failed": FAIL_COUNT,
            "success": all_passed,
            "details": {
                "gsheet": gsheet_pass,
                "gcal": gcal_pass,
                "email": email_pass,
            },
        }
        with open(res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    return all_passed, f"Passed: {PASS_COUNT}, Failed: {FAIL_COUNT}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    success, message = run_evaluation(
        args.agent_workspace,
        args.groundtruth_workspace,
        args.launch_time,
        args.res_log_file,
    )
    print(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
