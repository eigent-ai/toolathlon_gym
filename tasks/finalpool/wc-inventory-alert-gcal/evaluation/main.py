"""
Evaluation script for wc-inventory-alert-gcal task.

Checks:
1. Text file (out_of_stock_report.txt) matches groundtruth
2. Google Calendar events created for out-of-stock products
3. Email sent with out-of-stock summary
"""

import argparse
import json
import os
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

OOS_PRODUCT_IDS = [20, 39, 45, 71, 79]


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


# ============================================================================
# Check 1: out_of_stock_report.txt
# ============================================================================

def check_text_file(agent_workspace, groundtruth_workspace):
    print("\n=== Checking out_of_stock_report.txt ===")

    agent_file = os.path.join(agent_workspace, "out_of_stock_report.txt")
    gt_file = os.path.join(groundtruth_workspace, "out_of_stock_report.txt")

    if not os.path.isfile(agent_file):
        record("Text file exists", False, f"Not found: {agent_file}")
        return False
    record("Text file exists", True)

    with open(agent_file) as f:
        agent_lines = [l.strip() for l in f.readlines() if l.strip()]
    with open(gt_file) as f:
        gt_lines = [l.strip() for l in f.readlines() if l.strip()]

    record("Line count matches (5)", len(agent_lines) == len(gt_lines),
           f"Expected {len(gt_lines)}, got {len(agent_lines)}")

    # Check each product ID appears
    matched = 0
    for pid in OOS_PRODUCT_IDS:
        found = any(str(pid) in l.split(" - ")[0] for l in agent_lines)
        record(f"Report: product {pid} listed", found, f"ID {pid} not found")
        if found:
            matched += 1

    return matched == len(OOS_PRODUCT_IDS)


# ============================================================================
# Check 2: Google Calendar events
# ============================================================================

def check_gcal():
    print("\n=== Checking Google Calendar ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT summary, description, start_datetime
        FROM gcal.events
        ORDER BY summary
    """)
    events = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[check_gcal] Found {len(events)} calendar events.")

    record("At least 5 calendar events created", len(events) >= 5,
           f"Found {len(events)}")

    # Check events have "Restock:" in title
    restock_events = [e for e in events if "restock" in (e[0] or "").lower()]
    record("At least 5 restock events", len(restock_events) >= 5,
           f"Found {len(restock_events)} with 'Restock' in title")

    # Check date is March 10, 2026
    march_10_events = []
    for summary, description, start_dt in restock_events:
        if start_dt:
            date_str = start_dt.strftime("%Y-%m-%d")
            if date_str == "2026-03-10":
                march_10_events.append(summary)

    record("Restock events on 2026-03-10", len(march_10_events) >= 5,
           f"Found {len(march_10_events)} on March 10")

    # Check descriptions mention product IDs
    for pid in OOS_PRODUCT_IDS:
        pid_str = str(pid)
        found = any(pid_str in (e[1] or "") for e in restock_events)
        record(f"gcal: event mentions product {pid}",
               found, f"Product {pid} not in any event description")

    return True


# ============================================================================
# Check 3: Email
# ============================================================================

def check_emails():
    print("\n=== Checking Emails ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
    """)
    all_emails = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[check_emails] Found {len(all_emails)} total emails.")
    record("At least 1 email sent", len(all_emails) >= 1, f"Found {len(all_emails)}")

    found = False
    for subject, from_addr, to_addr, body_text in all_emails:
        subject_lower = (subject or "").lower()
        if "out of stock" in subject_lower or "stock alert" in subject_lower:
            found = True

            from_str = str(from_addr or "").lower()
            record("email: from purchasing@ourstore.com",
                   "purchasing@ourstore.com" in from_str,
                   f"From: {from_addr}")

            to_str = str(to_addr or "").lower()
            record("email: to warehouse@ourstore.com",
                   "warehouse@ourstore.com" in to_str,
                   f"To: {to_addr}")

            body_lower = (body_text or "").lower()
            for pid in OOS_PRODUCT_IDS:
                record(f"email: body mentions product {pid}",
                       str(pid) in (body_text or ""),
                       f"Product {pid} not in email body")

            record("email: body mentions total count 5",
                   "5" in (body_text or ""),
                   "Total count not found")
            break

    record("email: stock alert email found", found,
           "No email with 'out of stock' in subject")

    return found


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    text_ok = check_text_file(args.agent_workspace, args.groundtruth_workspace)
    gcal_ok = check_gcal()
    email_ok = check_emails()

    all_passed = text_ok and gcal_ok and email_ok

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    print(f"  Overall: {'PASS' if all_passed else 'FAIL'}")

    if args.res_log_file:
        result = {
            "passed": PASS_COUNT,
            "failed": FAIL_COUNT,
            "success": all_passed,
        }
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
