"""
Check that the agent created the correct Google Calendar study sessions.
"""

import os
import psycopg2
from datetime import datetime

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

# Expected study sessions based on Fall 2013 courses with due dates.
# Only courses with due dates get study sessions:
#   DDD-2013J: exam 2014-06-19 -> sessions on 2014-06-17 15:00 and 2014-06-18 10:00
#   EEE-2013J: exam 2014-05-24 -> sessions on 2014-05-22 15:00 and 2014-05-23 10:00
#   FFF-2013J: exam 2014-05-25 -> sessions on 2014-05-23 15:00 and 2014-05-24 10:00
#   GGG-2013J: exam 2014-05-18 -> sessions on 2014-05-16 15:00 and 2014-05-17 10:00
EXPECTED_SESSIONS = [
    {
        "summary_contains": "DDD-2013J",
        "summary_contains_2": "Session 1",
        "start_date": "2014-06-17",
    },
    {
        "summary_contains": "DDD-2013J",
        "summary_contains_2": "Session 2",
        "start_date": "2014-06-18",
    },
    {
        "summary_contains": "EEE-2013J",
        "summary_contains_2": "Session 1",
        "start_date": "2014-05-22",
    },
    {
        "summary_contains": "EEE-2013J",
        "summary_contains_2": "Session 2",
        "start_date": "2014-05-23",
    },
    {
        "summary_contains": "FFF-2013J",
        "summary_contains_2": "Session 1",
        "start_date": "2014-05-23",
    },
    {
        "summary_contains": "FFF-2013J",
        "summary_contains_2": "Session 2",
        "start_date": "2014-05-24",
    },
    {
        "summary_contains": "GGG-2013J",
        "summary_contains_2": "Session 1",
        "start_date": "2014-05-16",
    },
    {
        "summary_contains": "GGG-2013J",
        "summary_contains_2": "Session 2",
        "start_date": "2014-05-17",
    },
]


def check_gcal():
    """
    Verify that the correct study sessions were created in Google Calendar.
    Returns (pass: bool, error_msg: str or None).
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT summary, description, start_datetime, end_datetime
        FROM gcal.events
        ORDER BY start_datetime
    """)
    events = cur.fetchall()
    cur.close()
    conn.close()

    print(f"[check_gcal] Found {len(events)} calendar events.")
    for ev in events:
        print(f"  Event: {ev[0]} | {ev[2]} - {ev[3]}")

    if len(events) < len(EXPECTED_SESSIONS):
        return False, (
            f"Expected at least {len(EXPECTED_SESSIONS)} study sessions, "
            f"found {len(events)}"
        )

    differences = []
    matched = 0

    for expected in EXPECTED_SESSIONS:
        found = False
        for summary, description, start_dt, end_dt in events:
            summary_lower = (summary or "").lower()
            if (
                expected["summary_contains"].lower() in summary_lower
                and expected["summary_contains_2"].lower() in summary_lower
            ):
                # Check date
                if start_dt is not None:
                    start_date_str = start_dt.strftime("%Y-%m-%d")
                    if start_date_str == expected["start_date"]:
                        found = True
                        matched += 1
                        break
                    else:
                        # Date mismatch but summary matched
                        differences.append(
                            f"{expected['summary_contains']} "
                            f"{expected['summary_contains_2']}: "
                            f"expected date {expected['start_date']}, "
                            f"got {start_date_str}"
                        )
                        found = True  # Found but wrong date
                        break

        if not found:
            differences.append(
                f"Missing: {expected['summary_contains']} "
                f"{expected['summary_contains_2']} on "
                f"{expected['start_date']}"
            )

    if differences:
        return False, (
            f"Matched {matched}/{len(EXPECTED_SESSIONS)} sessions. "
            f"Issues: {'; '.join(differences[:5])}"
        )

    print(f"[check_gcal] All {matched} study sessions verified.")
    return True, None
