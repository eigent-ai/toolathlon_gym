"""Preprocess for sf-sales-territory-realign-ppt-gsheet-email.
Clears writable schemas (gsheet, email) and injects noise data.
Copies initial_workspace files to agent_workspace.
"""
import argparse
import os
import shutil
import uuid

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Clear writable schemas
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.sheets")
    cur.execute("DELETE FROM gsheet.spreadsheets")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages WHERE folder_id != 0")
    conn.commit()

    # Inject noise spreadsheets
    sid1 = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s)",
        (sid1, "Q3 Marketing Budget")
    )
    cur.execute(
        "INSERT INTO gsheet.sheets (spreadsheet_id, title, index) VALUES (%s, %s, %s) RETURNING id",
        (sid1, "Sheet1", 0)
    )
    sheet1_id = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value) VALUES (%s, %s, %s, %s, %s)",
        (sid1, sheet1_id, 0, 0, "Department")
    )
    cur.execute(
        "INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value) VALUES (%s, %s, %s, %s, %s)",
        (sid1, sheet1_id, 0, 1, "Budget")
    )

    sid2 = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s)",
        (sid2, "Employee Training Log")
    )
    cur.execute(
        "INSERT INTO gsheet.sheets (spreadsheet_id, title, index) VALUES (%s, %s, %s) RETURNING id",
        (sid2, "Sheet1", 0)
    )
    sheet2_id = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value) VALUES (%s, %s, %s, %s, %s)",
        (sid2, sheet2_id, 0, 0, "Employee")
    )

    sid3 = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s)",
        (sid3, "Old Territory Notes")
    )
    cur.execute(
        "INSERT INTO gsheet.sheets (spreadsheet_id, title, index) VALUES (%s, %s, %s)",
        (sid3, "Sheet1", 0)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Cleared gsheet/email tables and injected noise data.")

    if args.agent_workspace:
        initial_ws = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "initial_workspace")
        for f in os.listdir(initial_ws):
            src = os.path.join(initial_ws, f)
            if os.path.isfile(src) and not f.startswith("."):
                shutil.copy2(src, os.path.join(args.agent_workspace, f))
        print(f"Copied initial_workspace files to {args.agent_workspace}")


if __name__ == "__main__":
    main()
