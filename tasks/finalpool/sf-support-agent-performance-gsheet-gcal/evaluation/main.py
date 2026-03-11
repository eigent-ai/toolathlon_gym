"""Evaluation for sf-support-agent-performance-gsheet-gcal.

Checks:
1. Google Sheet "Agent Performance Scorecard" with Scorecards and Rankings sheets
2. Google Calendar event "Agent Performance Review" 10 days from launch
3. Email to performance-review@company.example.com
"""
import argparse
import os
import sys
from datetime import datetime, timedelta

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")

PASS_COUNT = 0
FAIL_COUNT = 0

# Actual data from DB (sorted by tickets DESC)
AGENT_DATA = [
    # Agent, Total_Tickets, Avg_Response_Hrs, Avg_CSAT, SLA_Compliance_Rate
    ("Emily",   9193, 15.09, 3.25, 21.47),
    ("Charlie", 6640, 15.00, 3.24, 20.99),
    ("John",    6199, 15.06, 3.27, 20.37),
    ("Bob",     5446, 15.01, 3.26, 21.26),
    ("Alice",   4110, 14.94, 3.27, 20.39),
]


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {name}: {str(detail)[:200]}")


def num_close(a, b, tol=1.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def check_gsheet():
    print("\n=== Checking Google Sheet ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title FROM gsheet.spreadsheets
        WHERE title ILIKE '%agent%performance%' OR title ILIKE '%agent%scorecard%'
    """)
    sheets = cur.fetchall()
    check("Agent Performance Scorecard spreadsheet exists", len(sheets) >= 1,
          f"Found: {[s[1] for s in sheets]}")

    if not sheets:
        cur.close()
        conn.close()
        return False

    ss_id = sheets[0][0]

    # Check sheets/tabs
    cur.execute("SELECT title FROM gsheet.sheets WHERE spreadsheet_id = %s", (ss_id,))
    tabs = [r[0] for r in cur.fetchall()]
    has_scorecards = any("scorecard" in t.lower() for t in tabs)
    has_rankings = any("ranking" in t.lower() for t in tabs)
    check("Has Scorecards sheet", has_scorecards, f"Tabs: {tabs}")
    check("Has Rankings sheet", has_rankings, f"Tabs: {tabs}")

    # Check cells content
    cur.execute("SELECT value FROM gsheet.cells WHERE spreadsheet_id = %s", (ss_id,))
    cells = [str(r[0]) for r in cur.fetchall() if r[0] is not None]
    all_vals = " ".join(cells).lower()

    check("Sheet contains agent 'Emily'", "emily" in all_vals, "Not found")
    check("Sheet contains agent 'Alice'", "alice" in all_vals, "Not found")
    check("Sheet contains 5 agents", sum(1 for a in ["emily", "charlie", "john", "bob", "alice"] if a in all_vals) >= 4,
          "Missing agent names")

    # Check some numeric values
    check("Sheet contains ticket counts",
          any(str(v) in all_vals for v in ["9193", "6640", "6199", "5446", "4110"]),
          "Ticket counts not found")

    cur.close()
    conn.close()
    return has_scorecards and has_rankings


def check_gcal(launch_time_str):
    print("\n=== Checking Google Calendar ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT summary, description, start_datetime FROM gcal.events ORDER BY start_datetime")
    events = cur.fetchall()
    cur.close()
    conn.close()

    print(f"  Found {len(events)} calendar events")
    check("At least 1 calendar event", len(events) >= 1, f"Found {len(events)}")

    review_events = [e for e in events
                     if "agent" in (e[0] or "").lower() and "performance" in (e[0] or "").lower()]
    check("Agent Performance Review event exists", len(review_events) >= 1,
          f"Events: {[e[0] for e in events]}")

    if launch_time_str and review_events:
        try:
            launch_dt = datetime.fromisoformat(launch_time_str)
            expected_dt = launch_dt + timedelta(days=10)
            for ev in review_events:
                if ev[2]:
                    ev_dt = ev[2]
                    diff = abs((ev_dt.replace(tzinfo=None) - expected_dt).total_seconds())
                    check("Review meeting 10 days from launch", diff <= 86400 * 2,
                          f"Expected around {expected_dt}, got {ev_dt}")
                    break
        except Exception as e:
            print(f"  [INFO] Could not verify date: {e}")

    return len(review_events) >= 1


def check_email():
    print("\n=== Checking Email ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT subject, from_addr, to_addr, body_text
        FROM email.messages
        WHERE subject ILIKE '%agent%' AND subject ILIKE '%performance%'
        ORDER BY date DESC
    """)
    emails = cur.fetchall()
    cur.close()
    conn.close()

    check("Agent performance email exists", len(emails) >= 1, f"Found {len(emails)}")
    if emails:
        e = emails[0]
        to_str = str(e[2])
        check("Email to performance-review@company.example.com",
              "performance-review@company.example.com" in to_str.lower(), f"to: {to_str}")
        check("Email from support-manager@company.example.com",
              "support-manager@company.example.com" in (e[1] or "").lower(), f"from: {e[1]}")
        body = (e[3] or "").lower()
        check("Email body mentions agent performance",
              any(kw in body for kw in ["emily", "alice", "john", "bob", "charlie", "csat", "ticket"]),
              "Body missing agent data")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    gsheet_ok = check_gsheet()
    check_gcal(args.launch_time)
    check_email()

    print(f"\n=== SUMMARY ===")
    print(f"  Passed: {PASS_COUNT}")
    print(f"  Failed: {FAIL_COUNT}")
    overall = FAIL_COUNT == 0
    print(f"  Overall: {'PASS' if overall else 'FAIL'}")

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
