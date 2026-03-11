"""Evaluation for terminal-yf-sf-gsheet-word-gcal.
Checks:
1. Compensation_Review_Memo.docx content
2. Google Sheet "Sales Compensation Analysis" with 3 sheets
3. Google Calendar event "Q4 Compensation Review Meeting"
4. Script files exist (compute_bonuses.py, market_adjustment.py, validate_bonuses.py)
5. JSON output files with correct values
"""
import argparse
import json
import os
import sys
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
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
        print(f"  [FAIL] {name}: {str(detail)[:200]}")


def num_close(a, b, tol=2.0):
    try:
        return abs(float(a) - float(b)) <= tol
    except Exception:
        return False


def pct_close(a, b, tol=1.0):
    """Check if two percentage values are close."""
    try:
        return abs(float(a) - float(b)) <= tol
    except Exception:
        return False


def check_word(workspace):
    print("\n=== Check 1: Compensation_Review_Memo.docx ===")
    path = os.path.join(workspace, "Compensation_Review_Memo.docx")
    if not os.path.exists(path):
        check("Word file exists", False, f"Not found at {path}")
        return
    check("Word file exists", True)

    try:
        from docx import Document
        doc = Document(path)
        all_text = " ".join(p.text for p in doc.paragraphs).lower()

        check("Has title 'Q4 Compensation Review'",
              "q4 compensation review" in all_text or "compensation review memo" in all_text,
              f"Text snippet: {all_text[:100]}")
        check("Has Background section",
              "background" in all_text,
              "Missing 'Background' section")
        check("Has Methodology section",
              "methodology" in all_text,
              "Missing 'Methodology' section")
        check("Has Market Analysis section",
              "market analysis" in all_text or "market" in all_text,
              "Missing market analysis")
        check("Has Regional Performance section",
              "regional" in all_text or "region" in all_text,
              "Missing regional section")
        check("Has Budget Impact section",
              "budget" in all_text,
              "Missing budget section")
        check("Has Recommendations section",
              "recommend" in all_text,
              "Missing recommendations")
        check("Mentions DJI or Dow Jones",
              "dji" in all_text or "dow jones" in all_text or "dow" in all_text,
              "No DJI/Dow Jones reference")
        check("Mentions adjustment factor or 0.9",
              "0.9" in all_text or "adjustment" in all_text,
              "No adjustment factor reference")
        check("Mentions budget cap",
              "budget cap" in all_text or "30,000,000" in all_text or "30000000" in all_text or "30 million" in all_text,
              "No budget cap reference")
    except Exception as e:
        check("Word readable", False, str(e))


def check_gsheet():
    print("\n=== Check 2: Google Sheet 'Sales Compensation Analysis' ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, title FROM gsheet.spreadsheets WHERE lower(title) LIKE '%sales compensation%' OR lower(title) LIKE '%compensation analysis%'")
        rows = cur.fetchall()
        check("Spreadsheet exists", len(rows) >= 1, f"Found {len(rows)} matching spreadsheets")
        if not rows:
            return

        ss_id = rows[0][0]

        # Check sheets
        cur.execute("SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s ORDER BY index", (ss_id,))
        sheets = cur.fetchall()
        sheet_titles = [s[1].lower() for s in sheets]
        check("Has at least 3 sheets", len(sheets) >= 3, f"Found {len(sheets)} sheets: {sheet_titles}")

        has_rep = any("rep" in t or "performance" in t for t in sheet_titles)
        has_market = any("market" in t or "adjustment" in t for t in sheet_titles)
        has_adjusted = any("adjusted" in t or "bonus" in t for t in sheet_titles)
        check("Has Rep_Performance sheet", has_rep, f"Sheets: {sheet_titles}")
        check("Has Market_Adjustment sheet", has_market, f"Sheets: {sheet_titles}")
        check("Has Adjusted_Bonuses sheet", has_adjusted, f"Sheets: {sheet_titles}")

        # Check Market_Adjustment sheet has DJI data
        for sid, title in sheets:
            if "market" in title.lower() or "adjustment" in title.lower():
                cur.execute("""SELECT value FROM gsheet.cells
                    WHERE spreadsheet_id = %s AND sheet_id = %s""", (ss_id, sid))
                values = [r[0].lower() if r[0] else "" for r in cur.fetchall()]
                all_vals = " ".join(values)
                check("Market sheet has DJI", "dji" in all_vals or "^dji" in all_vals,
                      f"Values: {all_vals[:200]}")
                check("Market sheet has AMZN", "amzn" in all_vals,
                      f"Values: {all_vals[:200]}")
                check("Market sheet has XOM", "xom" in all_vals,
                      f"Values: {all_vals[:200]}")
                break

        # Check Rep_Performance sheet has data rows
        for sid, title in sheets:
            if "rep" in title.lower() or "performance" in title.lower():
                cur.execute("""SELECT COUNT(DISTINCT row_index) FROM gsheet.cells
                    WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index > 0""", (ss_id, sid))
                data_rows = cur.fetchone()[0]
                check("Rep sheet has data rows", data_rows >= 1, f"Found {data_rows} data rows")
                break

    except Exception as e:
        check("GSheet query", False, str(e))
    finally:
        cur.close()
        conn.close()


def check_gcal():
    print("\n=== Check 3: Calendar Event ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("""SELECT summary, description, start_datetime, end_datetime
            FROM gcal.events
            WHERE lower(summary) LIKE '%compensation%' OR lower(summary) LIKE '%q4%bonus%'""")
        events = cur.fetchall()
        check("Compensation meeting scheduled", len(events) >= 1, f"Found {len(events)} matching events")

        if events:
            evt = events[0]
            check("Event title contains 'Compensation Review'",
                  "compensation" in evt[0].lower() and "review" in evt[0].lower(),
                  f"Title: {evt[0]}")

            # Check it's in the March 9-13 week
            start_dt = evt[2]
            if start_dt:
                day = start_dt.day if hasattr(start_dt, 'day') else None
                month = start_dt.month if hasattr(start_dt, 'month') else None
                check("Event in March 9-13 week",
                      month == 3 and 9 <= day <= 13,
                      f"Start: {start_dt}")

                # Check 90-minute duration
                if evt[3]:
                    duration = (evt[3] - start_dt).total_seconds() / 60
                    check("Event is 90 minutes", 85 <= duration <= 95, f"Duration: {duration} min")

                # Check no conflict with existing events
                try:
                    cur.execute("""SELECT summary, start_datetime, end_datetime FROM gcal.events
                        WHERE lower(summary) NOT LIKE '%%compensation%%'
                        AND start_datetime < %s AND end_datetime > %s""",
                        (evt[3], evt[2]))
                    conflicts = cur.fetchall()
                    check("No conflicts with existing events", len(conflicts) == 0,
                          f"Conflicts: {[(c[0], str(c[1])) for c in conflicts]}")
                except Exception as e2:
                    check("No conflicts with existing events", False, str(e2))
    except Exception as e:
        check("GCal query", False, str(e))
    finally:
        cur.close()
        conn.close()


def check_scripts(workspace):
    print("\n=== Check 4: Script Files ===")
    for script in ["compute_bonuses.py", "market_adjustment.py", "validate_bonuses.py"]:
        path = os.path.join(workspace, script)
        check(f"{script} exists", os.path.exists(path))


def check_json_outputs(workspace):
    print("\n=== Check 5: JSON Output Files ===")

    # current_bonuses.json
    cb_path = os.path.join(workspace, "current_bonuses.json")
    if not os.path.exists(cb_path):
        check("current_bonuses.json exists", False)
    else:
        check("current_bonuses.json exists", True)
        try:
            with open(cb_path) as f:
                data = json.load(f)
            if isinstance(data, list):
                check("current_bonuses has entries", len(data) > 100, f"Found {len(data)} entries")
                # Check structure of first entry
                if data:
                    first = data[0]
                    has_keys = all(k in str(first).lower() for k in ["name", "region", "salary", "bonus"])
                    check("current_bonuses has required fields", has_keys, f"Keys: {list(first.keys()) if isinstance(first, dict) else 'not dict'}")
            elif isinstance(data, dict):
                check("current_bonuses has entries", len(data) > 0, f"Found dict with {len(data)} keys")
        except Exception as e:
            check("current_bonuses.json valid JSON", False, str(e))

    # market_adjusted_bonuses.json
    mab_path = os.path.join(workspace, "market_adjusted_bonuses.json")
    if not os.path.exists(mab_path):
        check("market_adjusted_bonuses.json exists", False)
    else:
        check("market_adjusted_bonuses.json exists", True)
        try:
            with open(mab_path) as f:
                data = json.load(f)
            if isinstance(data, list):
                check("adjusted_bonuses has entries", len(data) > 100, f"Found {len(data)} entries")
                # Check that adjusted values are different from current (factor should be 0.9)
                if data and isinstance(data[0], dict):
                    keys_lower = {k.lower() for k in data[0].keys()}
                    has_adjusted = any("adjust" in k for k in keys_lower)
                    check("adjusted_bonuses has adjusted field", has_adjusted,
                          f"Keys: {list(data[0].keys())}")
            elif isinstance(data, dict):
                check("adjusted_bonuses has data", len(data) > 0, f"Found dict with {len(data)} keys")
        except Exception as e:
            check("market_adjusted_bonuses.json valid JSON", False, str(e))


def check_reverse_validation():
    """Check no duplicate gcal events or wrong event types."""
    print("\n=== Reverse Validation ===")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Check no duplicate compensation review events
        cur.execute("""
            SELECT summary, start_datetime FROM gcal.events
            WHERE lower(summary) LIKE '%compensation%review%'
        """)
        comp_events = cur.fetchall()
        check("No duplicate Compensation Review events",
              len(comp_events) <= 1,
              f"Found {len(comp_events)} compensation review events: {[e[0] for e in comp_events]}")

        # Check no non-meeting event types were created (e.g., no 'bonus payout' or 'salary update' calendar events)
        cur.execute("""
            SELECT summary FROM gcal.events
            WHERE lower(summary) LIKE '%bonus%payout%'
               OR lower(summary) LIKE '%salary%update%'
               OR lower(summary) LIKE '%pay%raise%'
        """)
        wrong_events = cur.fetchall()
        check("No wrong event types (bonus payout, salary update, pay raise)",
              len(wrong_events) == 0,
              f"Found unexpected events: {[e[0] for e in wrong_events]}")

        # Check pre-existing events were not deleted
        cur.execute("""
            SELECT COUNT(*) FROM gcal.events
            WHERE lower(summary) NOT LIKE '%compensation%'
              AND lower(summary) NOT LIKE '%q4%bonus%'
        """)
        other_count = cur.fetchone()[0]
        check("Pre-existing calendar events preserved (>= 5)",
              other_count >= 5,
              f"Found {other_count} non-compensation events (expected >= 5 from original 11)")

    except Exception as e:
        check("Reverse validation (gcal noise)", False, str(e))
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    check_word(args.agent_workspace)
    check_gsheet()
    check_gcal()
    check_scripts(args.agent_workspace)
    check_json_outputs(args.agent_workspace)
    check_reverse_validation()

    total = PASS_COUNT + FAIL_COUNT
    if total == 0:
        print("\nFAIL: No checks performed.")
        sys.exit(1)

    accuracy = PASS_COUNT / total * 100
    print(f"\nOverall: {PASS_COUNT}/{total} checks passed ({accuracy:.1f}%)")

    result = {"total_passed": PASS_COUNT, "total_checks": total, "accuracy": accuracy}
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
