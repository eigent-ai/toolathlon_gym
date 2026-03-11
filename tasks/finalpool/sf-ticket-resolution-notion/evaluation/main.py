"""
Evaluation for sf-ticket-resolution-notion.
Checks:
1. Notion database "Slow Response Tickets Tracker" with pages per priority
2. Email sent to support.manager@company.example.com with summary
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


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def num_close(a, b, tol=1.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def get_expected_data():
    """Query Snowflake mirror for expected slow response ticket stats."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT "PRIORITY",
               COUNT(*) as count,
               ROUND(AVG("RESPONSE_TIME_HOURS")::numeric, 2) as avg_resp,
               ROUND(AVG("SLA_HOURS")::numeric, 2) as avg_sla,
               ROUND(AVG("RESPONSE_TIME_HOURS" / "SLA_HOURS" * 100)::numeric, 2) as avg_util,
               ROUND(AVG("CUSTOMER_SATISFACTION")::numeric, 2) as avg_csat
        FROM sf_data."SUPPORT_CENTER__PUBLIC__TICKETS"
        WHERE "RESPONSE_TIME_HOURS" / "SLA_HOURS" > 0.5
        GROUP BY "PRIORITY"
        ORDER BY "PRIORITY"
    """)
    priority_stats = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) FROM sf_data."SUPPORT_CENTER__PUBLIC__TICKETS"
        WHERE "RESPONSE_TIME_HOURS" / "SLA_HOURS" > 0.5
    """)
    total_slow = cur.fetchone()[0]

    cur.execute('SELECT COUNT(*) FROM sf_data."SUPPORT_CENTER__PUBLIC__TICKETS"')
    total_all = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "total_slow": total_slow,
        "total_all": total_all,
        "slow_pct": round(total_slow / total_all * 100, 2),
        "by_priority": {r[0]: {"count": int(r[1]), "avg_resp": float(r[2]),
                                "avg_sla": float(r[3]), "avg_util": float(r[4]),
                                "avg_csat": float(r[5])} for r in priority_stats},
    }


def check_notion(expected):
    """Check Notion database and pages."""
    print("\n=== Checking Notion ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Check for database
    cur.execute("""
        SELECT id, title FROM notion.databases
        WHERE archived = false
    """)
    databases = cur.fetchall()

    found_db = None
    for db_id, title in databases:
        title_str = json.dumps(title).lower() if title else ""
        if "slow" in title_str or "ticket" in title_str or "response" in title_str:
            found_db = (db_id, title)
            break

    record("Notion database exists", found_db is not None,
           f"No database with 'slow'/'ticket'/'response' found among {len(databases)}")

    # Check for pages
    cur.execute("""
        SELECT id, properties FROM notion.pages
        WHERE archived = false AND in_trash = false
    """)
    pages = cur.fetchall()
    record("At least 3 pages exist", len(pages) >= 3, f"Found {len(pages)}")

    # Check for priority-specific pages
    all_page_text = ""
    for page_id, props in pages:
        props_str = json.dumps(props).lower() if props else ""
        all_page_text += " " + props_str

        # Check blocks for this page
        cur.execute("""
            SELECT block_data::text FROM notion.blocks
            WHERE parent_id = %s AND archived = false
        """, (page_id,))
        blocks = cur.fetchall()
        for b in blocks:
            all_page_text += " " + str(b[0]).lower()

    for priority in ["high", "medium", "low"]:
        record(f"Page/content mentions '{priority}' priority",
               priority in all_page_text,
               f"'{priority}' not found in pages/blocks")

    # Check for ticket counts in content
    for priority, stats in expected["by_priority"].items():
        count_str = str(stats["count"])
        record(f"Content mentions {priority} count ({count_str})",
               count_str in all_page_text,
               f"'{count_str}' not found")

    cur.close()
    conn.close()
    return found_db is not None


def check_email(expected):
    """Check email to support manager."""
    print("\n=== Checking Email ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT subject, from_addr, to_addr, body_text FROM email.messages")
    emails = cur.fetchall()
    record("At least 1 email sent", len(emails) >= 1, f"Found {len(emails)}")

    found = False
    for subject, from_addr, to_addr, body_text in emails:
        to_str = str(to_addr or "").lower()
        subject_lower = (subject or "").lower()
        if "support.manager@company.example.com" in to_str or \
           ("ticket" in subject_lower or "response" in subject_lower or "slow" in subject_lower):
            found = True
            record("Email to support manager",
                   "support.manager@company.example.com" in to_str,
                   f"To: {to_addr}")
            record("Email subject relevant",
                   "ticket" in subject_lower or "response" in subject_lower or "slow" in subject_lower,
                   f"Subject: {subject}")

            body_lower = (body_text or "").lower()
            record("Email body mentions total count",
                   str(expected["total_slow"]) in (body_text or ""),
                   f"Expected {expected['total_slow']} in body")
            record("Email body mentions priority breakdown",
                   "high" in body_lower and "low" in body_lower,
                   "Missing priority references")
            break

    if not found:
        record("Report email exists", False, "No relevant email found")

    cur.close()
    conn.close()
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    expected = get_expected_data()
    print(f"[eval] Total slow response: {expected['total_slow']}/{expected['total_all']} ({expected['slow_pct']}%)")

    notion_ok = check_notion(expected)
    email_ok = check_email(expected)

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    overall = PASS_COUNT > 0 and FAIL_COUNT == 0
    print(f"  Overall: {'PASS' if overall else 'FAIL'}")

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
