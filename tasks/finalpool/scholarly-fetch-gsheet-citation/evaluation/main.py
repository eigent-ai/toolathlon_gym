"""
Evaluation script for scholarly-fetch-gsheet-citation task.

Checks:
1. Google Sheet spreadsheet exists with "citation" or "impact" in title
2. Has 2 sheets: Author Rankings + Paper Details
3. Author Rankings has correct author data sorted by total citations desc
4. Paper Details has correct paper data sorted by citations desc

Usage:
  python -m evaluation.main --agent_workspace <path>
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


def check(name: str, condition: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        detail_truncated = (detail[:200] + "...") if len(detail) > 200 else detail
        print(f"  [FAIL] {name}: {detail_truncated}")


def num_close(a, b, tolerance=0.15):
    """Check if two numbers are within tolerance (relative)."""
    try:
        a_val = float(str(a).replace(",", ""))
        b_val = float(b)
        if b_val == 0:
            return a_val == 0
        return abs(a_val - b_val) / b_val <= tolerance
    except (TypeError, ValueError):
        return False


def compute_expected_data():
    """Query scholarly.scholar_papers and compute expected author/paper data."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT title, authors, citation_count, pub_year FROM scholarly.scholar_papers")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    papers = []
    author_stats = {}
    for title, authors_json, citation_count, pub_year in rows:
        if isinstance(authors_json, str):
            authors_list = json.loads(authors_json)
        else:
            authors_list = authors_json
        author_names = [a.get("name", "Unknown") for a in authors_list]
        papers.append({
            "title": title,
            "authors": author_names,
            "citation_count": citation_count or 0,
            "year": pub_year,
        })
        for name in author_names:
            if name not in author_stats:
                author_stats[name] = {"total_citations": 0, "paper_count": 0}
            author_stats[name]["total_citations"] += citation_count or 0
            author_stats[name]["paper_count"] += 1

    for name, stats in author_stats.items():
        stats["avg_citations"] = round(
            stats["total_citations"] / max(stats["paper_count"], 1), 1
        )

    # Sort authors by total citations desc
    ranked_authors = sorted(
        author_stats.items(), key=lambda x: x[1]["total_citations"], reverse=True
    )

    # Sort papers by citation count desc
    papers_sorted = sorted(papers, key=lambda x: x["citation_count"], reverse=True)

    return ranked_authors, papers_sorted


def get_cells_for_sheet(cur, ss_id, sheet_id):
    """Fetch all cells for a sheet."""
    cur.execute("""
        SELECT row_index, col_index, value FROM gsheet.cells
        WHERE spreadsheet_id = %s AND sheet_id = %s
        ORDER BY row_index, col_index
    """, (ss_id, sheet_id))
    cells = {}
    for row_idx, col_idx, value in cur.fetchall():
        cells[(row_idx, col_idx)] = value
    return cells


def build_table(cells):
    """Build header list and data rows from cells dict."""
    if not cells:
        return [], []
    max_row = max(r for r, c in cells.keys())
    max_col = max(c for r, c in cells.keys())

    headers = []
    for col in range(max_col + 1):
        headers.append(str(cells.get((0, col), "")).strip())

    rows = []
    for row in range(1, max_row + 1):
        row_data = {}
        for col in range(max_col + 1):
            val = str(cells.get((row, col), "")).strip()
            if col < len(headers) and headers[col]:
                row_data[headers[col]] = val
            row_data[f"col_{col}"] = val
        rows.append(row_data)

    return headers, rows


def find_column(headers, candidates):
    """Find a column header matching any candidate (case-insensitive)."""
    for h in headers:
        h_lower = h.lower().replace(" ", "_").replace("-", "_")
        for c in candidates:
            c_lower = c.lower().replace(" ", "_").replace("-", "_")
            if c_lower in h_lower or h_lower in c_lower:
                return h
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=True)
    parser.add_argument("--groundtruth_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    parser.add_argument("--res_log_file", type=str, required=False)
    args = parser.parse_args()

    # Compute expected data from scholarly DB
    ranked_authors, papers_sorted = compute_expected_data()

    # -----------------------------------------------------------------------
    # Check 1: Google Sheet exists with relevant title
    # -----------------------------------------------------------------------
    print("\n--- Check 1: Google Sheet exists ---")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title FROM gsheet.spreadsheets
        WHERE LOWER(title) LIKE '%citation%'
           OR LOWER(title) LIKE '%impact%'
    """)
    spreadsheets = cur.fetchall()
    check("Google Sheet with 'citation' or 'impact' in title exists",
          len(spreadsheets) > 0, "No matching spreadsheet found")

    if not spreadsheets:
        cur.close()
        conn.close()
        total = PASS_COUNT + FAIL_COUNT
        print(f"\nResults: {PASS_COUNT}/{total} passed, {FAIL_COUNT} failed")
        sys.exit(1)

    ss_id = spreadsheets[0][0]
    ss_title = spreadsheets[0][1]
    print(f"  Found spreadsheet: '{ss_title}' (id={ss_id})")

    # -----------------------------------------------------------------------
    # Check 2: Has 2 sheets
    # -----------------------------------------------------------------------
    print("\n--- Check 2: Sheet count ---")
    cur.execute("SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s", (ss_id,))
    all_sheets = cur.fetchall()
    check("Spreadsheet has at least 2 sheets", len(all_sheets) >= 2,
          f"Found {len(all_sheets)} sheets: {[s[1] for s in all_sheets]}")

    # -----------------------------------------------------------------------
    # Check 3: Author Rankings sheet
    # -----------------------------------------------------------------------
    print("\n--- Check 3: Author Rankings sheet ---")
    cur.execute("""
        SELECT id, title FROM gsheet.sheets
        WHERE spreadsheet_id = %s AND (LOWER(title) LIKE %s OR LOWER(title) LIKE %s)
    """, (ss_id, '%author%', '%ranking%'))
    author_sheets = cur.fetchall()
    check("'Author Rankings' sheet exists", len(author_sheets) > 0,
          f"Sheets found: {[s[1] for s in all_sheets]}")

    if author_sheets:
        author_sheet_id = author_sheets[0][0]
        cells = get_cells_for_sheet(cur, ss_id, author_sheet_id)
        headers, rows = build_table(cells)
        non_empty_rows = [r for r in rows if any(v.strip() for v in r.values() if v)]

        # Check column headers
        name_col = find_column(headers, ["Author Name", "Author", "Name"])
        total_cit_col = find_column(headers, ["Total Citations", "Total_Citations", "Citations"])
        count_col = find_column(headers, ["Paper Count", "Paper_Count", "Papers", "Count"])
        avg_col = find_column(headers, ["Avg Citations Per Paper", "Avg_Citations", "Average", "Avg"])

        check("Author Rankings has Author Name column", name_col is not None, f"Headers: {headers}")
        check("Author Rankings has Total Citations column", total_cit_col is not None, f"Headers: {headers}")
        check("Author Rankings has Paper Count column", count_col is not None, f"Headers: {headers}")
        check("Author Rankings has Avg Citations column", avg_col is not None, f"Headers: {headers}")

        # Check row count matches expected unique authors
        expected_author_count = len(ranked_authors)
        check(f"Author Rankings has {expected_author_count} data rows (one per unique author)",
              len(non_empty_rows) >= expected_author_count,
              f"Found {len(non_empty_rows)} rows, expected {expected_author_count}")

        # Check top authors are correct
        if name_col and total_cit_col and len(non_empty_rows) >= 2:
            top_author_expected = ranked_authors[0][0]
            top_row_name = non_empty_rows[0].get(name_col, "")
            check("Top author by citations is correct",
                  top_author_expected.lower() in top_row_name.lower()
                  or top_row_name.lower() in top_author_expected.lower(),
                  f"Got '{top_row_name}', expected '{top_author_expected}'")

            # Check total citations of top author
            top_expected_cit = ranked_authors[0][1]["total_citations"]
            top_row_cit = non_empty_rows[0].get(total_cit_col, "")
            check("Top author total citations correct",
                  num_close(top_row_cit, top_expected_cit, tolerance=0.05),
                  f"Got '{top_row_cit}', expected {top_expected_cit}")

            # Check sort order (descending by total citations)
            try:
                cit_values = []
                for r in non_empty_rows:
                    val = r.get(total_cit_col, "").strip().replace(",", "")
                    if val:
                        cit_values.append(float(val))
                if len(cit_values) >= 2:
                    is_sorted_desc = all(cit_values[i] >= cit_values[i + 1]
                                         for i in range(len(cit_values) - 1))
                    check("Author Rankings sorted by total citations descending",
                          is_sorted_desc, f"Values: {cit_values[:6]}...")
            except (ValueError, TypeError):
                check("Total Citations column contains numeric values", False,
                      "Could not parse values")

    # -----------------------------------------------------------------------
    # Check 4: Paper Details sheet
    # -----------------------------------------------------------------------
    print("\n--- Check 4: Paper Details sheet ---")
    cur.execute("""
        SELECT id, title FROM gsheet.sheets
        WHERE spreadsheet_id = %s AND (LOWER(title) LIKE %s OR LOWER(title) LIKE %s)
    """, (ss_id, '%paper%', '%detail%'))
    paper_sheets = cur.fetchall()
    check("'Paper Details' sheet exists", len(paper_sheets) > 0,
          f"Sheets found: {[s[1] for s in all_sheets]}")

    if paper_sheets:
        paper_sheet_id = paper_sheets[0][0]
        cells = get_cells_for_sheet(cur, ss_id, paper_sheet_id)
        headers, rows = build_table(cells)
        non_empty_rows = [r for r in rows if any(v.strip() for v in r.values() if v)]

        # Check column headers
        title_col = find_column(headers, ["Paper Title", "Title", "Paper"])
        authors_col = find_column(headers, ["Authors", "Author"])
        cit_col = find_column(headers, ["Citation Count", "Citations", "Citation_Count", "Cited"])
        year_col = find_column(headers, ["Year", "Pub_Year"])

        check("Paper Details has Paper Title column", title_col is not None, f"Headers: {headers}")
        check("Paper Details has Authors column", authors_col is not None, f"Headers: {headers}")
        check("Paper Details has Citation Count column", cit_col is not None, f"Headers: {headers}")
        check("Paper Details has Year column", year_col is not None, f"Headers: {headers}")

        # Check row count
        expected_paper_count = len(papers_sorted)
        check(f"Paper Details has {expected_paper_count} data rows",
              len(non_empty_rows) >= expected_paper_count,
              f"Found {len(non_empty_rows)} rows, expected {expected_paper_count}")

        # Check top paper is correct
        if title_col and cit_col and len(non_empty_rows) >= 1:
            top_paper_expected = papers_sorted[0]["title"]
            top_row_title = non_empty_rows[0].get(title_col, "")
            check("Top paper by citations is correct",
                  top_paper_expected.lower() in top_row_title.lower()
                  or top_row_title.lower() in top_paper_expected.lower(),
                  f"Got '{top_row_title}', expected '{top_paper_expected}'")

            # Check sort order (descending by citations)
            try:
                cit_values = []
                for r in non_empty_rows:
                    val = r.get(cit_col, "").strip().replace(",", "")
                    if val:
                        cit_values.append(float(val))
                if len(cit_values) >= 2:
                    is_sorted_desc = all(cit_values[i] >= cit_values[i + 1]
                                         for i in range(len(cit_values) - 1))
                    check("Paper Details sorted by citations descending",
                          is_sorted_desc, f"Values: {cit_values[:6]}...")
            except (ValueError, TypeError):
                check("Citation Count column contains numeric values", False,
                      "Could not parse values")

        # Check that known paper titles appear
        if title_col:
            found_titles = [r.get(title_col, "").strip().lower() for r in non_empty_rows]
            matched = 0
            for p in papers_sorted:
                if any(p["title"].lower() in t or t in p["title"].lower()
                       for t in found_titles if t):
                    matched += 1
            check(f"At least {expected_paper_count - 1} papers present in Paper Details",
                  matched >= expected_paper_count - 1,
                  f"Matched {matched} of {expected_paper_count}")

    cur.close()
    conn.close()

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    total = PASS_COUNT + FAIL_COUNT
    print(f"\nResults: {PASS_COUNT}/{total} passed, {FAIL_COUNT} failed")

    if args.res_log_file:
        result = {
            "passed": PASS_COUNT,
            "failed": FAIL_COUNT,
            "pass_rate": round(PASS_COUNT / total, 3) if total > 0 else 0,
            "success": FAIL_COUNT == 0,
        }
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)

    if FAIL_COUNT == 0:
        print("All checks passed!")
    sys.exit(0 if FAIL_COUNT == 0 else 1)


if __name__ == "__main__":
    main()
