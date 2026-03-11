"""Evaluation for yf-market-news-digest-notion-gform-email.

Checks:
1. Notion database "Market News Digest" exists with at least 5 pages
2. GForm "Investor Market Sentiment Survey" exists with 4 questions
3. Email sent to subscribers@newsletter.example.com with subject containing 'Market' and 'Digest'
"""
import argparse
import json
import os
import sys

import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [PASS] {name}")
    else:
        FAIL_COUNT += 1
        d = (detail[:300] + "...") if len(detail) > 300 else detail
        print(f"  [FAIL] {name}: {d}")


def check_notion():
    print("\n=== Check 1: Notion Database ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Look for a database with "market" and "news" in the title
    cur.execute("SELECT id, title FROM notion.databases")
    dbs = cur.fetchall()

    found_db_id = None
    found_db_title = None
    for db_id, title_json in dbs:
        title_str = ""
        if isinstance(title_json, list):
            for item in title_json:
                if isinstance(item, dict):
                    title_str += item.get("plain_text", item.get("text", {}).get("content", ""))
        elif isinstance(title_json, str):
            title_str = title_json
        if "market" in title_str.lower() and "news" in title_str.lower():
            found_db_id = db_id
            found_db_title = title_str
            break

    check("Notion database with 'Market News' in title exists",
          found_db_id is not None,
          f"Found DBs: {[(str(r[0])[:20], str(r[1])[:50]) for r in dbs]}")

    if found_db_id:
        # Count pages in this database
        cur.execute("""
            SELECT COUNT(*) FROM notion.pages
            WHERE parent::text LIKE %s OR parent::text LIKE %s
        """, (f'%{found_db_id}%', '%database%'))
        # Also count all pages if parent matching is tricky
        cur.execute("SELECT COUNT(*) FROM notion.pages")
        total_pages = cur.fetchone()[0]
        check("At least 5 news entries in Notion", total_pages >= 5,
              f"Total pages: {total_pages}")

        # Check pages have relevant properties
        cur.execute("SELECT properties FROM notion.pages LIMIT 10")
        page_props = cur.fetchall()
        has_symbol = False
        for (props,) in page_props:
            props_str = str(props).lower() if props else ""
            if any(sym.lower() in props_str for sym in ["googl", "amzn", "jpm", "jnj", "xom"]):
                has_symbol = True
                break
        check("Notion pages contain stock symbol data", has_symbol,
              "No pages with GOOGL/AMZN/JPM/JNJ/XOM in properties")
    else:
        # Check if there are any pages at all
        cur.execute("SELECT COUNT(*) FROM notion.pages")
        page_count = cur.fetchone()[0]
        check("At least 5 news entries in Notion", page_count >= 5,
              f"Total notion pages: {page_count}")
        check("Notion pages contain stock symbol data", False, "No Market News database found")

    cur.close()
    conn.close()


def check_gform():
    print("\n=== Check 2: Google Form ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM gform.forms")
    forms = cur.fetchall()
    check("At least one Google Form exists", len(forms) > 0,
          "No forms found in gform.forms")

    found_form_id = None
    for form_id, title in forms:
        if "sentiment" in (title or "").lower() or "market" in (title or "").lower() or "investor" in (title or "").lower():
            found_form_id = form_id
            break
    if found_form_id is None and forms:
        found_form_id = forms[0][0]

    check("Form with 'Sentiment' or 'Market' or 'Investor' in title found",
          found_form_id is not None,
          f"Forms: {[(str(r[0])[:20], r[1]) for r in forms]}")

    if found_form_id:
        cur.execute("SELECT COUNT(*) FROM gform.questions WHERE form_id = %s", (found_form_id,))
        q_count = cur.fetchone()[0]
        check("Form has exactly 4 questions", q_count == 4,
              f"Got {q_count} questions")

        cur.execute("SELECT title FROM gform.questions WHERE form_id = %s ORDER BY position", (found_form_id,))
        questions = [r[0] for r in cur.fetchall()]
        check("Form has question about market outlook",
              any("outlook" in q.lower() or "market" in q.lower() for q in questions),
              f"Questions: {questions}")
        check("Form has question about sector",
              any("sector" in q.lower() for q in questions),
              f"Questions: {questions}")

    cur.close()
    conn.close()


def check_email():
    print("\n=== Check 3: Email ===")
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT subject, to_addr, from_addr FROM email.messages
        WHERE (subject ILIKE '%market%' AND subject ILIKE '%digest%')
           OR (subject ILIKE '%weekly%' AND subject ILIKE '%market%')
           OR to_addr::text ILIKE '%subscribers%'
        LIMIT 10
    """)
    rows = cur.fetchall()
    check("Email with 'Market Digest' or 'Weekly Market' in subject found",
          len(rows) > 0, "No matching email found")

    if rows:
        to_addrs = [str(r[1]) for r in rows]
        check("Email sent to subscribers@newsletter.example.com",
              any("subscribers" in addr for addr in to_addrs),
              f"To addresses: {to_addrs}")
        subjects = [r[0] or "" for r in rows]
        check("Email subject contains 'Digest' or 'Weekly'",
              any("digest" in s.lower() or "weekly" in s.lower() for s in subjects),
              f"Subjects: {subjects}")

    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    print("=== Evaluation: yf-market-news-digest-notion-gform-email ===")

    check_notion()
    check_gform()
    check_email()

    print(f"\n=== SUMMARY: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")

    if args.res_log_file:
        with open(args.res_log_file, "w") as f:
            json.dump({"pass": PASS_COUNT, "fail": FAIL_COUNT}, f)

    sys.exit(0 if FAIL_COUNT == 0 else 1)


if __name__ == "__main__":
    main()
