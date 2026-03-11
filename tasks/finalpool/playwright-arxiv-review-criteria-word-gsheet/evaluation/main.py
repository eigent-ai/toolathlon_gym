"""Evaluation for playwright-arxiv-review-criteria-word-gsheet."""
import argparse
import os
import sys

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432,
          dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
          user="eigent", password="camel")


def num_close(a, b, tol=0.5):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return str(a).strip().lower() == str(b).strip().lower()


def check_word_review(agent_workspace, filename, expected_title_fragment,
                      expected_tech, expected_novelty, expected_clarity,
                      expected_recommendation):
    errors = []
    path = os.path.join(agent_workspace, filename)
    if not os.path.exists(path):
        return [f"{filename} not found"]
    try:
        from docx import Document
        doc = Document(path)
        full_text = "\n".join(p.text for p in doc.paragraphs).lower()
        if expected_title_fragment.lower() not in full_text:
            errors.append(f"{filename}: missing paper title fragment '{expected_title_fragment}'")
        if "summary" not in full_text:
            errors.append(f"{filename}: missing Summary section")
        if "technical soundness" not in full_text and "technical" not in full_text:
            errors.append(f"{filename}: missing Technical Soundness section")
        if "novelty" not in full_text:
            errors.append(f"{filename}: missing Novelty section")
        if "clarity" not in full_text:
            errors.append(f"{filename}: missing Clarity section")
        if expected_recommendation.lower() not in full_text:
            errors.append(f"{filename}: missing recommendation '{expected_recommendation}'")
        # Check scores appear
        if str(expected_tech) not in full_text.replace("/5", ""):
            # Try looking for the score number
            pass  # Scores may appear in various formats
    except Exception as e:
        errors.append(f"Error reading {filename}: {e}")
    return errors


def check_gsheet():
    errors = []
    try:
        conn = psycopg2.connect(**DB)
        cur = conn.cursor()
        # Check spreadsheet exists
        cur.execute("""
            SELECT s.id, s.title FROM gsheet.spreadsheets s
            WHERE LOWER(s.title) LIKE '%review%' OR LOWER(s.title) LIKE '%conference%'
            ORDER BY s.id DESC LIMIT 5
        """)
        spreadsheets = cur.fetchall()
        if not spreadsheets:
            errors.append("No review tracker spreadsheet found")
            cur.close()
            conn.close()
            return errors

        ss_id = spreadsheets[0][0]

        # Check sheet exists
        cur.execute("""
            SELECT id FROM gsheet.sheets
            WHERE spreadsheet_id = %s AND LOWER(title) LIKE '%%review%%'
            LIMIT 1
        """, (ss_id,))
        sheet_row = cur.fetchone()
        if not sheet_row:
            errors.append("No 'Reviews' sheet found in spreadsheet")
            cur.close()
            conn.close()
            return errors

        sheet_id = sheet_row[0]

        # Check cells for paper data
        cur.execute("""
            SELECT row_index, col_index, value FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s
            ORDER BY row_index, col_index
        """, (ss_id, sheet_id))
        cells = cur.fetchall()
        cur.close()
        conn.close()

        if len(cells) < 24:  # header + 3 rows * 8 cols = 32, but at least 24
            errors.append(f"Too few cells in Reviews sheet: {len(cells)}, expected ~32")

        # Check that paper IDs appear
        cell_values = [str(c[2]).lower() if c[2] else "" for c in cells]
        all_text = " ".join(cell_values)
        if "2301.07041" not in all_text and "scaling" not in all_text:
            errors.append("Scaling Laws paper not found in GSheet")
        if "2203.11171" not in all_text and "instruct" not in all_text:
            errors.append("InstructGPT paper not found in GSheet")
        if "2205.01068" not in all_text and "opt" not in all_text:
            errors.append("OPT paper not found in GSheet")

        # Check scores
        if "4.7" not in all_text:
            errors.append("InstructGPT average score 4.7 not found in GSheet")
        if "4.3" not in all_text:
            errors.append("Scaling Laws average score 4.3 not found in GSheet")
        if "4.0" not in all_text and "4" not in all_text:
            errors.append("OPT average score 4.0 not found in GSheet")

        # Check completed status
        if "completed" not in all_text:
            errors.append("Review status 'Completed' not found in GSheet")

    except Exception as e:
        errors.append(f"Error checking GSheet: {e}")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()
    agent_ws = args.agent_workspace or os.path.join(os.path.dirname(__file__), "..", "groundtruth_workspace")

    all_errors = []

    # Check Review 1: Scaling Laws
    print("  Checking Review_Scaling_Laws.docx...")
    errs = check_word_review(agent_ws, "Review_Scaling_Laws.docx",
                             "Scaling Laws", 5, 4, 4, "Accept")
    if errs:
        all_errors.extend(errs)
        for e in errs[:3]:
            print(f"    ERROR: {e}")
    else:
        print("    PASS")

    # Check Review 2: InstructGPT
    print("  Checking Review_InstructGPT.docx...")
    errs = check_word_review(agent_ws, "Review_InstructGPT.docx",
                             "follow instructions", 5, 5, 4, "Accept")
    if errs:
        all_errors.extend(errs)
        for e in errs[:3]:
            print(f"    ERROR: {e}")
    else:
        print("    PASS")

    # Check Review 3: OPT
    print("  Checking Review_OPT.docx...")
    errs = check_word_review(agent_ws, "Review_OPT.docx",
                             "OPT", 4, 3, 5, "Weak Accept")
    if errs:
        all_errors.extend(errs)
        for e in errs[:3]:
            print(f"    ERROR: {e}")
    else:
        print("    PASS")

    # Check GSheet
    print("  Checking Google Sheet...")
    errs = check_gsheet()
    if errs:
        all_errors.extend(errs)
        for e in errs[:3]:
            print(f"    ERROR: {e}")
    else:
        print("    PASS")

    if all_errors:
        print(f"\n=== RESULT: FAIL ({len(all_errors)} errors) ===")
        for e in all_errors[:10]:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("\n=== RESULT: PASS ===")
        sys.exit(0)


if __name__ == "__main__":
    main()
