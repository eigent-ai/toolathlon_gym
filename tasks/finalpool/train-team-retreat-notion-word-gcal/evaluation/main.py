"""
Evaluation for train-team-retreat-notion-word-gcal task.

Checks:
1. Team_Retreat_Itinerary.docx exists with 4 sections
2. Notion page "Team Retreat March 2026" exists
3. 2 GCal events (Team Retreat Departs + Returns)
4. Email sent to hr@company.com
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
    print("\n=== Check 1: Team_Retreat_Itinerary.docx ===")

    docx_path = os.path.join(agent_workspace, "Team_Retreat_Itinerary.docx")
    if not os.path.exists(docx_path):
        record("Team_Retreat_Itinerary.docx exists", False, f"Not found at {docx_path}")
        return
    record("Team_Retreat_Itinerary.docx exists", True)

    try:
        from docx import Document
        doc = Document(docx_path)
    except Exception as e:
        record("Word file readable", False, str(e))
        return
    record("Word file readable", True)

    full_text = "\n".join(p.text for p in doc.paragraphs).lower()

    # Check sections
    has_overview = "retreat overview" in full_text or "overview" in full_text
    has_outbound = "outbound" in full_text
    has_return = "return" in full_text
    has_notes = "schedule" in full_text or "notes" in full_text
    record("Document has Retreat Overview section", has_overview, "Missing 'Retreat Overview'")
    record("Document has Outbound Journey section", has_outbound, "Missing 'Outbound'")
    record("Document has Return Journey section", has_return, "Missing 'Return'")
    record("Document has Schedule Notes section", has_notes, "Missing 'Schedule Notes'")

    # Check participant names
    has_alice = "alice" in full_text or "alice chen" in full_text
    has_bob = "bob" in full_text or "bob liu" in full_text
    has_david = "david" in full_text or "david zhang" in full_text
    record("Document mentions team members (Alice, Bob, David)", has_alice and has_bob and has_david,
           f"Alice:{has_alice}, Bob:{has_bob}, David:{has_david}")

    # Check train codes
    has_g235 = "g235" in full_text
    has_g168 = "g168" in full_text
    has_g236 = "g236" in full_text
    has_g167 = "g167" in full_text
    record("Document mentions outbound train codes (G235, G168)", has_g235 and has_g168,
           f"G235:{has_g235}, G168:{has_g168}")
    record("Document mentions return train codes (G236, G167)", has_g236 and has_g167,
           f"G236:{has_g236}, G167:{has_g167}")

    # Check destination
    has_qufu = "qufu" in full_text
    record("Document mentions Qufu as destination", has_qufu, "Qufu not found")


def check_notion():
    print("\n=== Check 2: Notion Page ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, properties FROM notion.pages
        WHERE properties::text ILIKE '%Team Retreat%' OR properties::text ILIKE '%retreat march%'
    """)
    pages = cur.fetchall()
    cur.close()
    conn.close()

    record("Notion page 'Team Retreat March 2026' exists", len(pages) >= 1,
           f"Found {len(pages)} matching pages")

    if pages:
        page_id = pages[0][0]
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT block_data FROM notion.blocks WHERE parent_id = %s", (page_id,))
        blocks = cur.fetchall()
        cur.close()
        conn.close()

        block_text = " ".join(str(b[0]) for b in blocks).lower()
        has_content = len(blocks) > 0
        record("Notion page has content blocks", has_content, f"Found {len(blocks)} blocks")

        if has_content:
            has_train = "g235" in block_text or "g168" in block_text or "qufu" in block_text
            record("Notion page mentions train codes or Qufu", has_train, block_text[:200])


def check_gcal():
    print("\n=== Check 3: Calendar Events ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT summary, start_datetime, end_datetime, description
        FROM gcal.events
        WHERE summary ILIKE '%retreat%'
        ORDER BY start_datetime
    """)
    events = cur.fetchall()
    cur.close()
    conn.close()

    record("At least 2 retreat calendar events", len(events) >= 2,
           f"Found {len(events)} events")

    depart_events = [e for e in events if "depart" in (e[0] or "").lower()]
    return_events = [e for e in events if "return" in (e[0] or "").lower() or "returns" in (e[0] or "").lower()]
    record("'Team Retreat Departs' event exists", len(depart_events) >= 1,
           f"Found: {[e[0] for e in events]}")
    record("'Team Retreat Returns' event exists", len(return_events) >= 1,
           f"Found: {[e[0] for e in events]}")

    if depart_events:
        ev = depart_events[0]
        desc = (ev[3] or "").lower()
        has_names = "alice" in desc or "bob" in desc or "carol" in desc
        record("Depart event description mentions team members", has_names,
               f"Description: {desc[:200]}")


def check_email():
    print("\n=== Check 4: Email to HR ===")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT to_addr, subject, body_text FROM email.messages
        WHERE subject ILIKE '%retreat%' OR subject ILIKE '%travel confirmed%'
    """)
    messages = cur.fetchall()
    cur.close()
    conn.close()

    all_msgs = list(messages)
    record("Email about retreat sent", len(all_msgs) >= 1,
           f"Found {len(all_msgs)} matching emails")

    if all_msgs:
        to_raw = all_msgs[0][0]
        to_str = str(to_raw).lower() if to_raw else ""
        record("Email addressed to hr@company.com", "hr@company.com" in to_str,
               f"To: {to_str[:100]}")


def main():
    parser = ArgumentParser()
    parser.add_argument("--agent_workspace", required=False, default=".")
    parser.add_argument("--groundtruth_workspace", required=False, default=".")
    parser.add_argument("--launch_time", required=False)
    parser.add_argument("--res_log_file", required=False)
    args = parser.parse_args()

    check_word(args.agent_workspace)
    check_notion()
    check_gcal()
    check_email()

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
