"""
Evaluation script for canvas-assignment-calendar task.

Checks:
1. Text file (assignment_schedule.txt) matches groundtruth
2. Google Calendar events created for each assignment
3. Email sent with consolidated schedule
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


def num_close(a, b, rel_tol=0.15, abs_tol=0.5):
    return abs(float(a) - float(b)) <= max(abs_tol, abs(float(b)) * rel_tol)


def str_match(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return str(a).strip().lower() == str(b).strip().lower()


# ============================================================================
# Check 1: assignment_schedule.txt
# ============================================================================

def check_text_file(agent_workspace, groundtruth_workspace):
    print("\n=== Checking assignment_schedule.txt ===")

    agent_file = os.path.join(agent_workspace, "assignment_schedule.txt")
    gt_file = os.path.join(groundtruth_workspace, "assignment_schedule.txt")

    if not os.path.isfile(agent_file):
        record("Text file exists", False, f"Not found: {agent_file}")
        return False
    record("Text file exists", True)

    if not os.path.isfile(gt_file):
        record("Groundtruth text file exists", False, f"Not found: {gt_file}")
        return False

    with open(agent_file) as f:
        agent_lines = [l.strip() for l in f.readlines() if l.strip()]
    with open(gt_file) as f:
        gt_lines = [l.strip() for l in f.readlines() if l.strip()]

    record("Line count matches", len(agent_lines) == len(gt_lines),
           f"Expected {len(gt_lines)}, got {len(agent_lines)}")

    # Check that each groundtruth line appears in agent output
    matched = 0
    for gt_line in gt_lines:
        gt_parts = [p.strip().lower() for p in gt_line.split(" - ")]
        found = False
        for agent_line in agent_lines:
            agent_parts = [p.strip().lower() for p in agent_line.split(" - ")]
            if len(agent_parts) >= 3 and len(gt_parts) >= 3:
                if (agent_parts[0] == gt_parts[0] and
                    agent_parts[1] == gt_parts[1] and
                    agent_parts[2] == gt_parts[2]):
                    found = True
                    break
        if found:
            matched += 1

    record(f"Assignment lines matched ({matched}/{len(gt_lines)})",
           matched >= len(gt_lines) * 0.9,
           f"Matched {matched} of {len(gt_lines)}")

    return matched == len(gt_lines)


# ============================================================================
# Check 2: Google Calendar events
# ============================================================================

def check_gcal():
    print("\n=== Checking Google Calendar ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT summary, description, start_datetime, end_datetime
        FROM gcal.events
        ORDER BY summary
    """)
    events = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[check_gcal] Found {len(events)} calendar events.")

    record("At least 50 calendar events created", len(events) >= 50,
           f"Found {len(events)}")

    # Spot check some specific events
    spot_checks = [
        "AAA-2014J",
        "BBB-2014J",
        "CCC-2014J",
        "DDD-2014J",
        "EEE-2014J",
        "FFF-2014J",
        "GGG-2014J",
    ]

    all_ok = True
    for code in spot_checks:
        code_events = [e for e in events if code.lower() in (e[0] or "").lower()]
        record(f"gcal: events exist for {code}",
               len(code_events) > 0,
               f"No events found for {code}")
        if not code_events:
            all_ok = False

    return all_ok


# ============================================================================
# Check 3: Email sent
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

    record("At least 1 email sent", len(all_emails) >= 1,
           f"Found {len(all_emails)}")

    all_ok = True
    found_schedule = False

    for subject, from_addr, to_addr, body_text in all_emails:
        subject_lower = (subject or "").lower()
        if "assignment schedule" in subject_lower or "fall 2014" in subject_lower:
            found_schedule = True

            from_str = str(from_addr or "").lower()
            record("email: from coordinator",
                   "coordinator@openuniversity.ac.uk" in from_str,
                   f"From: {from_addr}")

            to_str = str(to_addr or "").lower()
            record("email: to students",
                   "students@openuniversity.ac.uk" in to_str,
                   f"To: {to_addr}")

            body_lower = (body_text or "").lower()
            record("email: body mentions AAA-2014J",
                   "aaa-2014j" in body_lower,
                   "Missing AAA-2014J in body")
            record("email: body mentions GGG-2014J",
                   "ggg-2014j" in body_lower,
                   "Missing GGG-2014J in body")
            record("email: body mentions total count",
                   "52" in (body_text or ""),
                   "Missing total count of 52")
            break

    record("email: schedule email found", found_schedule,
           "No email with 'assignment schedule' in subject")
    if not found_schedule:
        all_ok = False

    return all_ok


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
