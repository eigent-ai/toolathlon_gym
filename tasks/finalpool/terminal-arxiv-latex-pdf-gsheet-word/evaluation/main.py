"""
Evaluation for terminal-arxiv-latex-pdf-gsheet-word task.

Checks:
1. Google Sheet "Paper Review Matrix" with 3 sheets (Review Scores, Methodology Comparison, Rankings)
2. Conference_Review_Summary.docx
3. Intermediate JSON files (methodology_analysis.json, comparison_matrix.json, final_rankings.json)
"""
import argparse
import json
import os
import sys

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432,
          dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
          user="eigent", password="camel")

PASS_COUNT = 0
FAIL_COUNT = 0

TARGET_IDS = {"2401.00101", "2401.00102", "2401.00103", "2401.00104"}
NOISE_IDS = {"2401.00201", "2401.00202"}

# Expected scores based on the paper content and rubric
EXPECTED_SCORES = {
    "2401.00101": {"novelty": 5, "methodology_rigor": 4, "experimental_completeness": 4, "clarity": 4, "significance": 5, "total": 22},
    "2401.00102": {"novelty": 3, "methodology_rigor": 3, "experimental_completeness": 4, "clarity": 4, "significance": 3, "total": 17},
    "2401.00103": {"novelty": 4, "methodology_rigor": 4, "experimental_completeness": 3, "clarity": 3, "significance": 4, "total": 18},
    "2401.00104": {"novelty": 4, "methodology_rigor": 3, "experimental_completeness": 3, "clarity": 4, "significance": 4, "total": 18},
}

EXPECTED_RECS = {
    "2401.00101": "Accept",
    "2401.00102": "Revise",
    "2401.00103": "Revise",
    "2401.00104": "Revise",
}


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
    except (TypeError, ValueError):
        return False


def check_gsheet():
    """Check Google Sheet via database."""
    print("\n=== Checking Google Sheet 'Paper Review Matrix' ===")
    try:
        conn = psycopg2.connect(**DB)
        cur = conn.cursor()

        # Find spreadsheet
        cur.execute("SELECT id, title FROM gsheet.spreadsheets WHERE LOWER(title) LIKE '%paper review%'")
        rows = cur.fetchall()
        check("Spreadsheet 'Paper Review Matrix' exists", len(rows) >= 1,
              f"Found {len(rows)} matching spreadsheets")
        if not rows:
            cur.close(); conn.close()
            return

        ss_id = rows[0][0]

        # Check sheets
        cur.execute("SELECT id, title FROM gsheet.sheets WHERE spreadsheet_id = %s", (ss_id,))
        sheets = cur.fetchall()
        sheet_names = {s[1].strip().lower(): s[0] for s in sheets}

        # Sheet 1: Review Scores
        review_key = None
        for name, sid in sheet_names.items():
            if "review" in name and "score" in name:
                review_key = sid
                break
        check("Sheet 'Review Scores' exists", review_key is not None,
              f"Sheets: {list(sheet_names.keys())}")

        if review_key is not None:
            cur.execute("""
                SELECT row_index, col_index, value FROM gsheet.cells
                WHERE spreadsheet_id = %s AND sheet_id = %s
                ORDER BY row_index, col_index
            """, (ss_id, review_key))
            cells = cur.fetchall()

            # Build grid
            grid = {}
            for r, c, v in cells:
                grid[(r, c)] = v

            # Check header row (row 0)
            headers = [grid.get((0, c), "") for c in range(8)]
            header_lower = [str(h).lower() for h in headers]
            check("Review Scores has Paper_ID column",
                  any("paper" in h and "id" in h for h in header_lower),
                  f"Headers: {headers}")
            check("Review Scores has Total_Score column",
                  any("total" in h for h in header_lower),
                  f"Headers: {headers}")

            # Check 4 data rows
            data_rows = set()
            for (r, c), v in grid.items():
                if r >= 1 and c == 0 and v:
                    data_rows.add(str(v).strip())
            check("Review Scores has 4 target papers",
                  data_rows.issuperset(TARGET_IDS) or len(data_rows) >= 4,
                  f"Found IDs: {data_rows}")

            # Check no noise papers
            noise_in_review = data_rows.intersection(NOISE_IDS)
            check("Review Scores excludes noise papers",
                  len(noise_in_review) == 0,
                  f"Found noise: {noise_in_review}")

            # Check total scores are reasonable (between 5 and 25)
            total_col = None
            for c in range(8):
                if "total" in str(grid.get((0, c), "")).lower():
                    total_col = c
                    break
            if total_col is not None:
                for r in range(1, 5):
                    val = grid.get((r, total_col))
                    if val is not None:
                        check(f"Row {r} total score in range",
                              5 <= float(val) <= 25,
                              f"Got {val}")

        # Sheet 2: Methodology Comparison
        method_key = None
        for name, sid in sheet_names.items():
            if "method" in name:
                method_key = sid
                break
        check("Sheet 'Methodology Comparison' exists", method_key is not None,
              f"Sheets: {list(sheet_names.keys())}")

        if method_key is not None:
            cur.execute("""
                SELECT row_index, col_index, value FROM gsheet.cells
                WHERE spreadsheet_id = %s AND sheet_id = %s
                ORDER BY row_index, col_index
            """, (ss_id, method_key))
            cells = cur.fetchall()
            grid = {}
            for r, c, v in cells:
                grid[(r, c)] = v

            data_rows = set()
            for (r, c), v in grid.items():
                if r >= 1 and c == 0 and v:
                    data_rows.add(str(v).strip())
            check("Methodology Comparison has target papers",
                  len(data_rows.intersection(TARGET_IDS)) >= 4,
                  f"Found: {data_rows}")

            # Check methods column has content
            methods_populated = 0
            for r in range(1, 5):
                val = grid.get((r, 2))  # Methods_Used column
                if val and len(str(val).strip()) > 0:
                    methods_populated += 1
            check("Methodology rows have methods content",
                  methods_populated >= 3,
                  f"Populated: {methods_populated}")

        # Sheet 3: Rankings
        rank_key = None
        for name, sid in sheet_names.items():
            if "rank" in name:
                rank_key = sid
                break
        check("Sheet 'Rankings' exists", rank_key is not None,
              f"Sheets: {list(sheet_names.keys())}")

        if rank_key is not None:
            cur.execute("""
                SELECT row_index, col_index, value FROM gsheet.cells
                WHERE spreadsheet_id = %s AND sheet_id = %s
                ORDER BY row_index, col_index
            """, (ss_id, rank_key))
            cells = cur.fetchall()
            grid = {}
            for r, c, v in cells:
                grid[(r, c)] = v

            headers = [str(grid.get((0, c), "")).lower() for c in range(5)]
            check("Rankings has Recommendation column",
                  any("recommend" in h for h in headers),
                  f"Headers: {headers}")

            # Check recommendations
            rec_col = None
            for c in range(5):
                if "recommend" in str(grid.get((0, c), "")).lower():
                    rec_col = c
                    break
            if rec_col is not None:
                recs = set()
                for r in range(1, 5):
                    val = grid.get((r, rec_col))
                    if val:
                        recs.add(str(val).strip().lower())
                check("Rankings has Accept/Revise/Reject values",
                      recs.issubset({"accept", "revise", "reject"}) and len(recs) >= 2,
                      f"Found: {recs}")

                # Check at least one Accept
                check("At least one paper recommended Accept",
                      "accept" in recs,
                      f"Recommendations: {recs}")

        cur.close()
        conn.close()
    except Exception as e:
        check("GSheet check", False, str(e))


def check_word(agent_workspace):
    """Check Conference_Review_Summary.docx."""
    print("\n=== Checking Conference_Review_Summary.docx ===")
    docx_path = os.path.join(agent_workspace, "Conference_Review_Summary.docx")
    check("Conference_Review_Summary.docx exists", os.path.isfile(docx_path))
    if not os.path.isfile(docx_path):
        return
    try:
        from docx import Document
        doc = Document(docx_path)
        text = " ".join(p.text for p in doc.paragraphs).lower()
        check("Document has substantial content", len(text) > 500, f"Length: {len(text)}")

        # Check sections
        check("Contains 'overview' section",
              "overview" in text)
        check("Contains 'per-paper review' or individual reviews",
              "per-paper" in text or "per paper" in text or "2401.00101" in text)
        check("Contains 'comparative analysis'",
              "comparative" in text or "comparison" in text)
        check("Contains 'recommendation' section",
              "recommendation" in text)

        # Check paper references
        for pid in TARGET_IDS:
            check(f"Mentions paper {pid}", pid in text, "Not found in document")

        # Check key terms
        check("Mentions strengths/weaknesses",
              "strength" in text or "weakness" in text)
        check("Contains accept/revise/reject recommendations",
              ("accept" in text and "revise" in text) or "reject" in text)

        # Check no noise papers
        for nid in NOISE_IDS:
            check(f"Does not include noise paper {nid}",
                  nid not in text,
                  f"Found noise paper {nid}")

    except ImportError:
        check("python-docx available", False)
    except Exception as e:
        check("Word document readable", False, str(e))


def check_json_files(agent_workspace):
    """Check intermediate JSON files."""
    print("\n=== Checking Intermediate JSON Files ===")

    # methodology_analysis.json
    ma_path = os.path.join(agent_workspace, "methodology_analysis.json")
    check("methodology_analysis.json exists", os.path.isfile(ma_path))
    if os.path.isfile(ma_path):
        try:
            with open(ma_path) as f:
                ma = json.load(f)
            if isinstance(ma, list):
                ids = {str(e.get("paper_id", e.get("id", ""))).strip() for e in ma}
            elif isinstance(ma, dict):
                ids = set(ma.keys())
            else:
                ids = set()
            check("methodology_analysis has 4 target papers",
                  ids.issuperset(TARGET_IDS) or len(ids) >= 4,
                  f"Found: {ids}")
        except Exception as e:
            check("methodology_analysis readable", False, str(e))

    # comparison_matrix.json
    cm_path = os.path.join(agent_workspace, "comparison_matrix.json")
    check("comparison_matrix.json exists", os.path.isfile(cm_path))
    if os.path.isfile(cm_path):
        try:
            with open(cm_path) as f:
                cm = json.load(f)
            if isinstance(cm, list):
                ids = {str(e.get("paper_id", e.get("id", ""))).strip() for e in cm}
            elif isinstance(cm, dict):
                ids = set(cm.keys())
            else:
                ids = set()
            check("comparison_matrix has 4 target papers",
                  ids.issuperset(TARGET_IDS) or len(ids) >= 4,
                  f"Found: {ids}")
        except Exception as e:
            check("comparison_matrix readable", False, str(e))

    # final_rankings.json
    fr_path = os.path.join(agent_workspace, "final_rankings.json")
    check("final_rankings.json exists", os.path.isfile(fr_path))
    if os.path.isfile(fr_path):
        try:
            with open(fr_path) as f:
                fr = json.load(f)
            if isinstance(fr, list):
                check("final_rankings has 4 entries", len(fr) >= 4, f"Got {len(fr)}")
                # Check sorted by score descending
                if len(fr) >= 2:
                    scores = []
                    for e in fr:
                        s = e.get("total_score", e.get("total", e.get("score", 0)))
                        scores.append(float(s) if s else 0)
                    check("final_rankings sorted by score descending",
                          all(scores[i] >= scores[i+1] for i in range(len(scores)-1)),
                          f"Scores: {scores}")
                # Check recommendations present
                recs = {str(e.get("recommendation", "")).lower() for e in fr}
                check("final_rankings has recommendations",
                      recs.intersection({"accept", "revise", "reject"}),
                      f"Found: {recs}")
        except Exception as e:
            check("final_rankings readable", False, str(e))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    check_gsheet()
    check_word(args.agent_workspace)
    check_json_files(args.agent_workspace)

    total = PASS_COUNT + FAIL_COUNT
    accuracy = PASS_COUNT / total * 100 if total > 0 else 0
    print(f"\nOverall: {PASS_COUNT}/{total} ({accuracy:.1f}%)")
    result = {"total_passed": PASS_COUNT, "total_checks": total, "accuracy": accuracy}
    if args.res_log_file:
        with open(args.res_log_file, "w") as f:
            json.dump(result, f, indent=2)
    sys.exit(0 if accuracy >= 70 else 1)


if __name__ == "__main__":
    main()
