"""
Evaluation for scholarly-reading-group-gcal-gsheet-word task.
Checks: GSheet reading schedule, GCal events, Word document.
"""
import argparse
import os
import sys

import psycopg2
from docx import Document

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}

PASS_COUNT = 0
FAIL_COUNT = 0

TRANSFORMER_KEYWORDS = ["attention is all you need", "bert", "language models are few-shot", "gpt"]


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def check_gsheet():
    print("\n=== Checking Google Sheet ===")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("SELECT id, title FROM gsheet.spreadsheets")
        spreadsheets = cur.fetchall()

        target_ss = None
        for sid, title in spreadsheets:
            if title and ("transformer" in title.lower() or "reading group" in title.lower()):
                target_ss = sid
                break

        record("GSheet 'Transformer Reading Group Schedule' exists",
               target_ss is not None,
               f"Found sheets: {[t for _, t in spreadsheets]}")

        if target_ss is None:
            conn.close()
            return

        cur.execute("SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s", (target_ss,))
        sheets = cur.fetchall()
        if not sheets:
            record("GSheet has at least one sheet", False)
            conn.close()
            return

        sheet_id = sheets[0][0]
        cur.execute("""
            SELECT COUNT(DISTINCT row_index) FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s AND row_index > 0
        """, (target_ss, sheet_id))
        data_rows = cur.fetchone()[0]
        record("GSheet has at least 3 paper rows (one per week)", data_rows >= 3,
               f"Found {data_rows} data rows")

        # Check paper content in cells
        cur.execute("""
            SELECT LOWER(value) FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s
        """, (target_ss, sheet_id))
        cell_values = [row[0] for row in cur.fetchall() if row[0]]
        all_text = " ".join(cell_values)

        has_attention = "attention is all you need" in all_text or "attention" in all_text
        has_bert = "bert" in all_text
        has_gpt = "few-shot" in all_text or "gpt" in all_text or "language models are" in all_text
        record("GSheet contains Attention paper entry", has_attention)
        record("GSheet contains BERT paper entry", has_bert)
        record("GSheet contains few-shot/GPT paper entry", has_gpt)

        conn.close()
    except Exception as e:
        record("GSheet connection", False, str(e))


def check_gcal():
    print("\n=== Checking Google Calendar ===")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            SELECT summary, start_datetime FROM gcal.events
            WHERE LOWER(summary) LIKE '%reading group%' OR LOWER(summary) LIKE '%transformer%'
            ORDER BY start_datetime
        """)
        events = cur.fetchall()
        record("GCal has at least 3 Reading Group events", len(events) >= 3,
               f"Found {len(events)} events: {[(e[0], str(e[1])[:10]) for e in events]}")

        if len(events) >= 3:
            # Check dates are in March 2026
            dates = [str(e[1])[:10] for e in events]
            has_march16 = any("2026-03-16" in d for d in dates)
            has_march23 = any("2026-03-23" in d for d in dates)
            has_march30 = any("2026-03-30" in d for d in dates)
            record("GCal has event on March 16 2026", has_march16, f"Dates found: {dates}")
            record("GCal has event on March 23 2026", has_march23, f"Dates found: {dates}")
            record("GCal has event on March 30 2026", has_march30, f"Dates found: {dates}")

            # Check time is 3pm (15:00) UTC by extracting UTC hour
            cur.execute("""
                SELECT EXTRACT(HOUR FROM start_datetime AT TIME ZONE 'UTC') as utc_hour
                FROM gcal.events
                WHERE LOWER(summary) LIKE '%reading group%' OR LOWER(summary) LIKE '%transformer%'
            """)
            hours = [int(row[0]) for row in cur.fetchall()]
            has_correct_time = any(h == 15 for h in hours)
            record("GCal events scheduled at 3pm UTC", has_correct_time, f"UTC hours found: {hours}")

        conn.close()
    except Exception as e:
        record("GCal connection", False, str(e))


def check_word(agent_workspace):
    print("\n=== Checking Word Document ===")
    doc_path = os.path.join(agent_workspace, "Transformer_Reading_List.docx")
    if not os.path.isfile(doc_path):
        record("Word file Transformer_Reading_List.docx exists", False, f"Not found at: {doc_path}")
        return
    record("Word file Transformer_Reading_List.docx exists", True)

    try:
        doc = Document(doc_path)
    except Exception as e:
        record("Word file readable", False, str(e))
        return
    record("Word file readable", True)

    full_text = "\n".join(p.text for p in doc.paragraphs).lower()

    has_heading = "transformer" in full_text and ("reading group" in full_text or "reading list" in full_text or "architecture" in full_text)
    record("Word has 'Transformer' heading with reading group context", has_heading)

    has_intro = len(full_text) > 300
    record("Word has substantial content", has_intro, f"Text length: {len(full_text)}")

    has_attention = "attention is all you need" in full_text or ("attention" in full_text and "vaswani" in full_text)
    has_bert = "bert" in full_text and ("devlin" in full_text or "bidirectional" in full_text)
    has_fewshot = "few-shot" in full_text or "few shot" in full_text or "gpt-3" in full_text or "language models are" in full_text

    papers_mentioned = sum([has_attention, has_bert, has_fewshot])
    record("Word mentions 'Attention Is All You Need'", has_attention)
    record("Word mentions BERT", has_bert)
    record("Word mentions few-shot learners (GPT-3)", has_fewshot)
    record("Word mentions at least 2 of the 3 transformer papers", papers_mentioned >= 2,
           f"Found {papers_mentioned}/3 papers")

    # Check for week assignments
    has_week = "week 1" in full_text or "week 2" in full_text or "week1" in full_text
    record("Word assigns papers to reading group weeks", has_week)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=True)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--res_log_file", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    check_gsheet()
    check_gcal()
    check_word(args.agent_workspace)

    total = PASS_COUNT + FAIL_COUNT
    print(f"\n=== Results: {PASS_COUNT}/{total} passed ===")
    if FAIL_COUNT > 0:
        print(f"{FAIL_COUNT} checks failed")
        sys.exit(1)
    else:
        print("All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
