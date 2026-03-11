"""Evaluation for canvas-module-completion-notion-gcal."""
import argparse
import json
import os
import sys

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        detail_str = f": {detail[:200]}" if detail else ""
        print(f"  [FAIL] {name}{detail_str}")


def check_notion():
    """Check Notion database creation."""
    print("\n=== Checking Notion Database ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM notion.databases")
    dbs = cur.fetchall()
    check("At least one Notion database created", len(dbs) >= 1,
          f"Found {len(dbs)} databases")

    db_id = None
    for did, title in dbs:
        title_str = ""
        if isinstance(title, list):
            for part in title:
                if isinstance(part, dict):
                    title_str += part.get("plain_text", "") or part.get("text", {}).get("content", "")
        elif isinstance(title, str):
            title_str = title
        elif title:
            title_str = str(title)
        if "ccc" in title_str.lower() or "module tracker" in title_str.lower() or "creative computing" in title_str.lower():
            db_id = did
            check("Notion database titled 'CCC Fall 2014 - Module Tracker'", True)
            break

    if db_id is None:
        check("Notion database titled 'CCC Fall 2014 - Module Tracker'", False,
              f"Found databases: {dbs}")

    # Check Notion pages for module entries
    cur.execute("SELECT COUNT(*) FROM notion.pages")
    page_count = cur.fetchone()[0]
    check("Notion pages created for modules", page_count >= 5,
          f"Found {page_count} pages")

    conn.close()


def check_gcal():
    """Check Google Calendar events."""
    print("\n=== Checking Google Calendar Events ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, summary, start_datetime FROM gcal.events ORDER BY start_datetime")
    events = cur.fetchall()
    check("At least 4 calendar events created", len(events) >= 4,
          f"Found {len(events)} events")

    review_events = [e for e in events if "module review" in (e[1] or "").lower() or "ccc" in (e[1] or "").lower()]
    check("At least 4 'CCC Module Review Meeting' events",
          len(review_events) >= 4,
          f"Review events: {[(e[1], str(e[2])) for e in review_events]}")

    conn.close()


def check_emails():
    """Check that setup email was sent."""
    print("\n=== Checking Emails ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT subject, from_addr, to_addr, body_text FROM email.messages")
    all_emails = cur.fetchall()
    conn.close()

    def find_email_for_recipient(recipient):
        for subj, from_addr, to_addr, body in all_emails:
            if to_addr:
                recipients = []
                if isinstance(to_addr, list):
                    recipients = [str(r).strip().lower() for r in to_addr]
                elif isinstance(to_addr, str):
                    try:
                        parsed = json.loads(to_addr)
                        if isinstance(parsed, list):
                            recipients = [str(r).strip().lower() for r in parsed]
                        else:
                            recipients = [str(to_addr).strip().lower()]
                    except (json.JSONDecodeError, TypeError):
                        recipients = [str(to_addr).strip().lower()]
                if recipient.lower() in recipients:
                    return subj, from_addr, to_addr, body
        return None

    result = find_email_for_recipient("teaching-team@ccc.example.com")
    check("Email sent to teaching-team@ccc.example.com", result is not None,
          f"Total emails: {len(all_emails)}")

    if result:
        subj, from_addr, to_addr, body = result
        check("Email subject contains 'Module Review Setup'",
              "module review setup" in (subj or "").lower(),
              f"Subject: {subj}")
        check("Email from ta@university.example.com",
              "ta@university.example.com" in (from_addr or "").lower(),
              f"From: {from_addr}")
        body_lower = (body or "").lower()
        check("Email mentions Creative Computing or CCC",
              "creative computing" in body_lower or "ccc" in body_lower,
              "Expected course name")
        check("Email mentions modules",
              "module" in body_lower,
              "Expected 'module' in email body")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    print("=" * 70)
    print("CANVAS MODULE COMPLETION NOTION GCAL - EVALUATION")
    print("=" * 70)

    check_notion()
    check_gcal()
    check_emails()

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    overall = FAIL_COUNT == 0
    print(f"  Overall: {'PASS' if overall else 'FAIL'}")
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
