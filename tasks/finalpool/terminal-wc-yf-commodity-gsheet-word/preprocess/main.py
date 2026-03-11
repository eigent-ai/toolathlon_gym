"""Preprocess for terminal-wc-yf-commodity-gsheet-word.
Clears gsheet schema. WC and YF are read-only.
"""
import argparse
import os
import uuid

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432,
          dbname=os.environ.get("PGDATABASE", "toolathlon_gym"), user="eigent", password="camel")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.permissions")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        conn.commit()
        print("[preprocess] Cleared gsheet schema.")

        # Inject gsheet noise
        ss_id = f"noise-{uuid.uuid4()}"
        cur.execute("INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s)", (ss_id, "Unrelated Budget Notes"))
        cur.execute("INSERT INTO gsheet.sheets (spreadsheet_id, title, index) VALUES (%s, %s, 0) RETURNING id", (ss_id, "Notes"))
        sh_id = cur.fetchone()[0]
        cur.execute("INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value) VALUES (%s, %s, 1, 1, 'Random budget notes')", (ss_id, sh_id))
        conn.commit()
        print("[preprocess] Injected noise data.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
