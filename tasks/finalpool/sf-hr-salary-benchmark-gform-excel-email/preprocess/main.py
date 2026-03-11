"""Preprocess for sf-hr-salary-benchmark-gform-excel-email.
Clears writable schemas, copies initial_workspace files.
"""
import argparse
import os
import shutil
import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def clear_writable_schemas(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    cur.execute("DELETE FROM gcal.events")
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.sheets")
    cur.execute("DELETE FROM gsheet.spreadsheets")
    cur.execute("DELETE FROM gsheet.folders")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    cur.execute("DELETE FROM notion.blocks")
    cur.execute("DELETE FROM notion.comments")
    cur.execute("DELETE FROM notion.pages")
    cur.execute("DELETE FROM notion.databases")
    conn.commit()
    print("[preprocess] Writable schemas cleared.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    try:
        clear_writable_schemas(conn)
    finally:
        conn.close()

    if args.agent_workspace and os.path.exists(args.agent_workspace):
        initial_ws = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "initial_workspace")
        if os.path.exists(initial_ws):
            for f in os.listdir(initial_ws):
                src = os.path.join(initial_ws, f)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(args.agent_workspace, f))
                    print(f"[preprocess] Copied {f} to agent workspace.")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
