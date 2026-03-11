"""
Evaluation for arxiv-latex-review-notion-word task.
Checks: Notion page, Word document, GSheet.
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

PAPER_KEYWORDS = ["dpo", "direct preference", "llama", "mistral"]


def record(name, passed, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if passed:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        msg = f": {detail[:300]}" if detail else ""
        print(f"  [FAIL] {name}{msg}")


def check_notion():
    print("\n=== Checking Notion Page ===")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("""
            SELECT id, properties FROM notion.pages
            WHERE archived = false AND in_trash = false
        """)
        pages = cur.fetchall()

        target_page = None
        for pid, props in pages:
            props_text = str(props).lower() if props else ""
            if "llm fine-tuning" in props_text or ("llm" in props_text and "fine" in props_text and "tuning" in props_text):
                target_page = pid
                break
            if "fine-tuning knowledge base" in props_text or "knowledge base" in props_text:
                target_page = pid
                break

        record("Notion page 'LLM Fine-Tuning Knowledge Base' exists",
               target_page is not None,
               f"Searched {len(pages)} pages")

        if target_page is None:
            # Try broader search
            for pid, props in pages:
                props_text = str(props).lower() if props else ""
                if "fine" in props_text or "llm" in props_text or "tuning" in props_text:
                    target_page = pid
                    break
            if target_page:
                print(f"  [INFO] Found page with broader search: {target_page}")

        # Check that multiple paper-related pages exist or content is substantial
        paper_pages = 0
        for pid, props in pages:
            props_text = str(props).lower() if props else ""
            if any(kw in props_text for kw in ["dpo", "llama", "mistral", "preference", "fine-tun"]):
                paper_pages += 1

        record("Notion has pages/content for at least 2 relevant papers",
               paper_pages >= 2 or len(pages) >= 3,
               f"Found {paper_pages} paper-related pages, {len(pages)} total pages")

        conn.close()
    except Exception as e:
        record("Notion connection", False, str(e))


def check_word(agent_workspace):
    print("\n=== Checking Word Document ===")
    doc_path = os.path.join(agent_workspace, "LLM_Paper_Synthesis.docx")
    if not os.path.isfile(doc_path):
        record("Word file LLM_Paper_Synthesis.docx exists", False, f"Not found at: {doc_path}")
        return
    record("Word file LLM_Paper_Synthesis.docx exists", True)

    try:
        doc = Document(doc_path)
    except Exception as e:
        record("Word file readable", False, str(e))
        return
    record("Word file readable", True)

    full_text = "\n".join(p.text for p in doc.paragraphs).lower()

    has_heading = ("llm" in full_text or "fine-tun" in full_text) and ("survey" in full_text or "synthesis" in full_text or "alignment" in full_text)
    record("Word has heading mentioning LLM fine-tuning/alignment", has_heading)

    has_intro = len(full_text) > 400
    record("Word has substantial content", has_intro, f"Text length: {len(full_text)}")

    has_dpo = "dpo" in full_text or "direct preference" in full_text
    has_llama = "llama" in full_text
    has_mistral = "mistral" in full_text
    papers_mentioned = sum([has_dpo, has_llama, has_mistral])

    record("Word mentions DPO paper", has_dpo)
    record("Word mentions Llama 2 paper", has_llama)
    record("Word mentions Mistral 7B paper", has_mistral)
    record("Word mentions at least 2 relevant papers", papers_mentioned >= 2,
           f"Found {papers_mentioned}/3 papers")


def check_gsheet():
    print("\n=== Checking Google Sheet ===")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("SELECT id, title FROM gsheet.spreadsheets")
        spreadsheets = cur.fetchall()

        target_ss = None
        for sid, title in spreadsheets:
            if title and ("llm" in title.lower() or "paper" in title.lower()) and ("registry" in title.lower() or "paper" in title.lower()):
                target_ss = sid
                break

        record("GSheet 'LLM Paper Registry' exists",
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
        record("GSheet 'LLM Paper Registry' has at least 3 data rows",
               data_rows >= 3, f"Found {data_rows} data rows")

        cur.execute("""
            SELECT LOWER(value) FROM gsheet.cells
            WHERE spreadsheet_id = %s AND sheet_id = %s
        """, (target_ss, sheet_id))
        cell_values = [row[0] for row in cur.fetchall() if row[0]]
        all_text = " ".join(cell_values)

        has_dpo = "dpo" in all_text or "direct preference" in all_text
        has_llama = "llama" in all_text
        has_mistral = "mistral" in all_text
        record("GSheet contains DPO paper entry", has_dpo)
        record("GSheet contains Llama paper entry", has_llama)
        record("GSheet contains Mistral paper entry", has_mistral)

        conn.close()
    except Exception as e:
        record("GSheet connection", False, str(e))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=True)
    parser.add_argument("--groundtruth_workspace", required=False)
    parser.add_argument("--res_log_file", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    check_notion()
    check_word(args.agent_workspace)
    check_gsheet()

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
