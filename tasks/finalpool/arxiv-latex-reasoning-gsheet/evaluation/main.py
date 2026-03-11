"""
Evaluation for arxiv-latex-reasoning-gsheet task.
Checks Google Sheet and Word document.
"""
import argparse
import json
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

# The 5 reasoning papers from arxiv_latex.papers
EXPECTED_REASONING_PAPERS = [
    {"id": "2201.11903", "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"},
    {"id": "2203.11171", "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models"},
    {"id": "2205.11916", "title": "Large Language Models are Zero-Shot Reasoners"},
    {"id": "2210.03493", "title": "Automatic Chain of Thought Prompting in Large Language Models"},
    {"id": "2305.10601", "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"},
]

PAPER_KEYWORDS = [
    ["chain-of-thought prompting", "chain of thought prompting"],
    ["self-consistency"],
    ["zero-shot"],
    ["automatic chain", "auto-cot"],
    ["tree of thoughts"],
]

# Word embedding papers that should NOT be included
NOISE_KEYWORDS = ["word2vec", "glove", "word representation", "skip-gram"]


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
    """Check Google Sheet exists with correct data."""
    print("\n=== Checking Google Sheet ===")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Find spreadsheet
        cur.execute("SELECT id, title FROM gsheet.spreadsheets")
        spreadsheets = cur.fetchall()

        target_ss = None
        for sid, title in spreadsheets:
            if title and "reasoning" in title.lower():
                target_ss = sid
                break

        record("Google Sheet 'Reasoning Methods Comparison' exists",
               target_ss is not None,
               f"Found spreadsheets: {[t for _, t in spreadsheets]}")

        if target_ss is None:
            conn.close()
            return

        # Check "Papers" sheet exists
        cur.execute("""
            SELECT id, title FROM gsheet.sheets
            WHERE spreadsheet_id = %s
        """, (target_ss,))
        sheets = cur.fetchall()
        sheet_names = [t for _, t in sheets]

        papers_sheet_id = None
        for sid, sname in sheets:
            if sname and sname.strip().lower() == "papers":
                papers_sheet_id = sid
                break

        record("Sheet 'Papers' exists", papers_sheet_id is not None,
               f"Found sheets: {sheet_names}")

        if papers_sheet_id is None:
            conn.close()
            return

        # Read cells from Papers sheet
        cur.execute("""
            SELECT row_index, col_index, value FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s
            ORDER BY row_index, col_index
        """, (target_ss, papers_sheet_id))
        cells = cur.fetchall()

        # Build grid
        grid = {}
        for row_idx, col_idx, val in cells:
            if row_idx not in grid:
                grid[row_idx] = {}
            grid[row_idx][col_idx] = val

        if not grid:
            record("Papers sheet has data", False, "No cells found")
            conn.close()
            return

        min_row = min(grid.keys())
        header_row = grid.get(min_row, {})
        header_vals = [header_row.get(i, "") for i in range(max(header_row.keys()) + 1)] if header_row else []

        # Find Title column
        title_col = None
        for i, h in enumerate(header_vals):
            if h and str(h).strip().lower() == "title":
                title_col = i
                break

        record("Title column exists", title_col is not None, f"Header: {header_vals}")

        # Check Method column
        method_col = None
        for i, h in enumerate(header_vals):
            if h and str(h).strip().lower() == "method":
                method_col = i
                break
        record("Method column exists", method_col is not None, f"Header: {header_vals}")

        # Check Key_Contribution column
        kc_col = None
        for i, h in enumerate(header_vals):
            if h and "contribution" in str(h).strip().lower():
                kc_col = i
                break
        record("Key_Contribution column exists", kc_col is not None, f"Header: {header_vals}")

        # Check data rows
        data_rows = {r: grid[r] for r in grid if r > min_row}
        record("Papers sheet has 5 data rows", len(data_rows) == 5,
               f"Found {len(data_rows)} rows")

        # Check paper titles are present
        if title_col is not None:
            found_titles = []
            for r in sorted(data_rows.keys()):
                val = data_rows[r].get(title_col, "")
                if val:
                    found_titles.append(str(val).lower())

            for paper in EXPECTED_REASONING_PAPERS:
                t_lower = paper["title"].lower()
                found = any(t_lower in t or t in t_lower for t in found_titles)
                record(f"Has paper: {paper['title'][:50]}...", found)

        conn.close()
    except Exception as e:
        record("GSheet connection", False, str(e))


def check_word(agent_workspace):
    """Check Word document."""
    print("\n=== Checking Word Document ===")
    doc_path = os.path.join(agent_workspace, "Reasoning_Methods_Review.docx")

    if not os.path.isfile(doc_path):
        record("Word file exists", False, f"Not found: {doc_path}")
        return

    record("Word file exists", True)

    try:
        doc = Document(doc_path)
    except Exception as e:
        record("Word file readable", False, str(e))
        return

    record("Word file readable", True)

    full_text = "\n".join(p.text for p in doc.paragraphs)
    full_lower = full_text.lower()

    # Check title
    has_title = "chain-of-thought" in full_lower and "reasoning" in full_lower and "comparison" in full_lower
    if not has_title:
        has_title = "chain of thought" in full_lower and "methods" in full_lower
    record("Word doc has correct title", has_title)

    # Check date
    has_date = "2026-03-06" in full_text or "march 6, 2026" in full_lower or "march 2026" in full_lower
    record("Word doc has date", has_date)

    # Check each reasoning paper is mentioned
    for i, paper in enumerate(EXPECTED_REASONING_PAPERS):
        found = any(kw in full_lower for kw in PAPER_KEYWORDS[i])
        record(f"Word mentions: {paper['title'][:50]}...", found,
               f"Keywords: {PAPER_KEYWORDS[i]}")

    # Check noise papers NOT mentioned
    for noise in NOISE_KEYWORDS:
        absent = noise not in full_lower
        record(f"Word does NOT mention: {noise}", absent)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=True)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--res_log_file", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    check_gsheet()
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
