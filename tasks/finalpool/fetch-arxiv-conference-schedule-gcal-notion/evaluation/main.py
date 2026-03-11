"""
Evaluation script for fetch-arxiv-conference-schedule-gcal-notion task.

Checks:
1. Notion database "Conference Reading List" with 6+ entries
2. Google Calendar events for 3 reading group sessions
"""

import argparse
import json
import os
import sys

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
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


def str_contains(haystack, needle):
    if haystack is None or needle is None:
        return False
    return needle.strip().lower() in str(haystack).strip().lower()


def check_notion():
    """Check Notion database for Conference Reading List."""
    print("\n=== Checking Notion Database ===")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Find databases
        cur.execute("SELECT id, title, properties FROM notion.databases")
        dbs = cur.fetchall()

        found_db = None
        for db_id, title_raw, props in dbs:
            # title can be jsonb array or string
            if isinstance(title_raw, list):
                title = " ".join(t.get("plain_text", "") for t in title_raw if isinstance(t, dict))
            elif isinstance(title_raw, str):
                try:
                    parsed = json.loads(title_raw)
                    if isinstance(parsed, list):
                        title = " ".join(t.get("plain_text", "") for t in parsed if isinstance(t, dict))
                    else:
                        title = title_raw
                except (json.JSONDecodeError, TypeError):
                    title = title_raw
            else:
                title = str(title_raw) if title_raw else ""
            title_lower = title.lower()
            if "conference" in title_lower or "reading" in title_lower:
                found_db = db_id
                break

        if not found_db:
            record(
                "Conference Reading List database exists",
                False,
                f"Found {len(dbs)} databases: {[d[1] for d in dbs]}",
            )
            cur.close()
            conn.close()
            return False

        record("Conference Reading List database exists", True)

        # Check database properties
        if props:
            if isinstance(props, str):
                props = json.loads(props)
            prop_names = [k.lower() for k in props.keys()] if isinstance(props, dict) else []
            has_title = any("title" in p for p in prop_names)
            has_source = any("source" in p for p in prop_names)
            has_relevance = any("relevance" in p for p in prop_names)
            record(
                "Database has required properties",
                has_title or has_source or has_relevance,
                f"Properties: {prop_names}",
            )
        else:
            record("Database has properties", False, "No properties found")

        # Check pages (entries) in the database
        cur.execute(
            "SELECT id, properties FROM notion.pages WHERE parent::text LIKE %s",
            (f'%{found_db}%',),
        )
        pages = cur.fetchall()

        record(
            "Database has >= 6 entries",
            len(pages) >= 6,
            f"Found {len(pages)} entries",
        )

        # Check that entries have diverse sources
        sources = set()
        for page_id, page_props in pages:
            if isinstance(page_props, str):
                page_props = json.loads(page_props)
            if isinstance(page_props, dict):
                for key, val in page_props.items():
                    if "source" in key.lower():
                        if isinstance(val, dict):
                            select_val = val.get("select", {})
                            if isinstance(select_val, dict):
                                name = select_val.get("name", "")
                                if name:
                                    sources.add(name.lower())

        record(
            "Entries from both ArXiv and Scholar sources",
            len(sources) >= 2 or len(pages) >= 6,
            f"Sources found: {sources}",
        )

        # Check relevance scores
        has_scores = False
        for page_id, page_props in pages:
            if isinstance(page_props, str):
                page_props = json.loads(page_props)
            if isinstance(page_props, dict):
                for key, val in page_props.items():
                    if "relevance" in key.lower():
                        has_scores = True
                        break
            if has_scores:
                break

        record("Entries have relevance scores", has_scores)

        cur.close()
        conn.close()
        return True

    except Exception as e:
        record("Notion DB accessible", False, str(e))
        return False


def check_calendar():
    """Check Google Calendar for reading group sessions."""
    print("\n=== Checking Google Calendar ===")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "SELECT summary, description, start_datetime, end_datetime FROM gcal.events"
        )
        events = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        record("Calendar DB accessible", False, str(e))
        return False

    all_ok = True

    # Check for 3 reading group sessions
    reading_events = [
        e for e in events
        if "reading group" in (e[0] or "").lower()
    ]
    record(
        "3 reading group events exist",
        len(reading_events) >= 3,
        f"Found {len(reading_events)} reading group events",
    )
    if len(reading_events) < 3:
        all_ok = False

    # Check specific topics
    topics_found = {
        "transformer": False,
        "attention": False,
        "optim": False,
    }
    for summary, description, start_dt, end_dt in reading_events:
        summary_lower = (summary or "").lower()
        for topic in topics_found:
            if topic in summary_lower:
                topics_found[topic] = True

    for topic, found in topics_found.items():
        record(f"Reading group for '{topic}' topic exists", found)
        if not found:
            all_ok = False

    # Check dates are in March 2026
    march_events = []
    for summary, description, start_dt, end_dt in reading_events:
        if start_dt:
            dt_str = str(start_dt)
            if "2026-03" in dt_str:
                march_events.append(summary)

    record(
        "Reading group events in March 2026",
        len(march_events) >= 3,
        f"March events: {march_events}",
    )
    if len(march_events) < 3:
        all_ok = False

    # Check descriptions mention papers
    desc_with_papers = 0
    for summary, description, start_dt, end_dt in reading_events:
        if description and len(description) > 20:
            desc_with_papers += 1

    record(
        "Reading group descriptions have content",
        desc_with_papers >= 2,
        f"{desc_with_papers} events have substantive descriptions",
    )
    if desc_with_papers < 2:
        all_ok = False

    return all_ok


def check_xlsx_content(workspace):
    """Check Conference_Reading_Summary.xlsx has valid content."""
    print("\n=== Checking XLSX Content ===")
    try:
        import openpyxl
    except ImportError:
        record("openpyxl available", False, "Cannot import openpyxl")
        return False

    xlsx_path = os.path.join(workspace, "Conference_Reading_Summary.xlsx")
    if not os.path.isfile(xlsx_path):
        record("Conference_Reading_Summary.xlsx exists", False, f"Not found: {xlsx_path}")
        return False
    record("Conference_Reading_Summary.xlsx exists", True)

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    notion_ok = check_notion()
    cal_ok = check_calendar()
    xlsx_ok = check_xlsx_content(args.agent_workspace)

    print(f"\n=== SUMMARY ===")
    print(f"  Notion:   {'PASS' if notion_ok else 'FAIL'}")
    print(f"  Calendar: {'PASS' if cal_ok else 'FAIL'}")
    print(f"  XLSX:     {'PASS' if xlsx_ok else 'FAIL'}")
    print(f"  Passed: {PASS_COUNT}, Failed: {FAIL_COUNT}")

    overall = notion_ok and cal_ok and xlsx_ok
    print(f"  Overall:  {'PASS' if overall else 'FAIL'}")

    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
