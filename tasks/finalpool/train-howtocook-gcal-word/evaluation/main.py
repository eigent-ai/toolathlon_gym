"""
Evaluation for train-howtocook-gcal-word task.

Checks:
1. Qufu_Trip_Itinerary.docx exists with required sections
2. Document mentions G235 and G236 train codes
3. Document mentions recipe names
4. GCal has 3 events: outbound train, return train, cultural visit
5. GCal outbound event on 2026-03-12 titled with G235
6. GCal return event on 2026-03-15 titled with G236
7. GCal cultural visit event on 2026-03-13
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


def check_word(agent_workspace):
    print("\n=== Check 1: Qufu_Trip_Itinerary.docx ===")
    docx_path = os.path.join(agent_workspace, "Qufu_Trip_Itinerary.docx")
    if not os.path.exists(docx_path):
        record("Qufu_Trip_Itinerary.docx exists", False, f"Not found at {docx_path}")
        return
    record("Qufu_Trip_Itinerary.docx exists", True)

    try:
        import docx
        doc = docx.Document(docx_path)
        full_text = " ".join(p.text for p in doc.paragraphs).lower()
    except Exception as e:
        record("Word document readable", False, str(e))
        return
    record("Word document readable", True)

    record("Contains Trip Overview section", "trip overview" in full_text,
           "No 'Trip Overview' found")
    record("Contains Outbound Journey section",
           "outbound" in full_text or "outbound journey" in full_text,
           "No 'Outbound Journey' found")
    record("Contains Return Journey section", "return" in full_text and "journey" in full_text,
           "No return journey section found")
    record("Contains Meal Plan section", "meal plan" in full_text or "meal" in full_text,
           "No 'Meal Plan' found")
    record("Mentions G235 train code", "g235" in full_text, "No G235 train code found")
    record("Mentions G236 train code", "g236" in full_text, "No G236 train code found")
    record("Mentions Qufu or Confucius",
           "qufu" in full_text or "confucius" in full_text,
           "No Qufu/Confucius mention found")

    # Check for recipe mention (congee/porridge)
    has_recipe = any(kw in full_text for kw in
                     ["congee", "porridge", "rice", "stir-fry", "stir fry", "vegetable"])
    record("Mentions recipe content from meal plan", has_recipe,
           "No recipe content (congee/porridge/stir-fry) found")


def check_gcal():
    print("\n=== Check 2: Google Calendar Events ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Check outbound train event on 2026-03-12
    cur.execute("""
        SELECT summary, start_datetime, end_datetime
        FROM gcal.events
        WHERE start_datetime >= '2026-03-12' AND start_datetime < '2026-03-13'
        ORDER BY start_datetime
    """)
    events_mar12 = cur.fetchall()
    train_events_12 = [e for e in events_mar12 if "g235" in (e[0] or "").lower()
                       or "beijing" in (e[0] or "").lower() or "qufu" in (e[0] or "").lower()
                       or "train" in (e[0] or "").lower()]
    record("Outbound train event exists on 2026-03-12", len(train_events_12) >= 1,
           f"Events on Mar 12: {[e[0] for e in events_mar12]}")

    if train_events_12:
        e = train_events_12[0]
        start_hour = e[1].hour if e[1] else -1
        record("Outbound event starts at 17:30", start_hour == 17,
               f"Start time: {e[1]}")

    # Check cultural visit on 2026-03-13
    cur.execute("""
        SELECT summary, start_datetime, end_datetime
        FROM gcal.events
        WHERE start_datetime >= '2026-03-13' AND start_datetime < '2026-03-14'
        ORDER BY start_datetime
    """)
    events_mar13 = cur.fetchall()
    cultural_events = [e for e in events_mar13 if
                       any(kw in (e[0] or "").lower() for kw in
                           ["confucius", "temple", "mansion", "cultural", "qufu"])]
    record("Cultural visit event on 2026-03-13", len(cultural_events) >= 1,
           f"Events on Mar 13: {[e[0] for e in events_mar13]}")

    # Check return train event on 2026-03-15
    cur.execute("""
        SELECT summary, start_datetime, end_datetime
        FROM gcal.events
        WHERE start_datetime >= '2026-03-15' AND start_datetime < '2026-03-16'
        ORDER BY start_datetime
    """)
    events_mar15 = cur.fetchall()
    return_events = [e for e in events_mar15 if "g236" in (e[0] or "").lower()
                     or "beijing" in (e[0] or "").lower() or "qufu" in (e[0] or "").lower()
                     or "train" in (e[0] or "").lower()]
    record("Return train event exists on 2026-03-15", len(return_events) >= 1,
           f"Events on Mar 15: {[e[0] for e in events_mar15]}")

    if return_events:
        e = return_events[0]
        start_hour = e[1].hour if e[1] else -1
        record("Return event starts at 15:00", start_hour == 15,
               f"Start time: {e[1]}")

    # Check total events created (at least 3)
    cur.execute("SELECT COUNT(*) FROM gcal.events WHERE start_datetime >= '2026-03-12'")
    total = cur.fetchone()[0]
    record("At least 3 calendar events created", total >= 3, f"Found {total} events")

    cur.close()
    conn.close()


def check_xlsx_content(workspace):
    """Check Trip_Reference.xlsx has valid content."""
    print("\n=== Checking XLSX Content ===")
    try:
        import openpyxl
    except ImportError:
        record("openpyxl available", False, "Cannot import openpyxl")
        return False

    xlsx_path = os.path.join(workspace, "Trip_Reference.xlsx")
    if not os.path.isfile(xlsx_path):
        record("Trip_Reference.xlsx exists", False, f"Not found: {xlsx_path}")
        return False
    record("Trip_Reference.xlsx exists", True)

    try:
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        record("XLSX has at least one sheet", len(wb.worksheets) >= 1,
               f"Found {len(wb.worksheets)} sheets")
        all_ok = True
        for ws in wb.worksheets:
            rows = list(ws.iter_rows(values_only=True))
            has_data = len(rows) >= 2
            record(f"XLSX sheet '{ws.title}' has data rows", has_data,
                   f"Only {len(rows)} rows")
            if not has_data:
                all_ok = False
        wb.close()
        return all_ok
    except Exception as e:
        record("XLSX readable", False, str(e))
        return False


def main():
    parser = ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    check_word(args.agent_workspace)
    check_gcal()
    check_xlsx_content(args.agent_workspace)

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
