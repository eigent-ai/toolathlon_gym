"""Preprocess for yf-portfolio-analysis-excel-word-email.
Clears writable schemas (email) for a clean state and copies initial workspace files.
YF data is read-only and does not need injection.
"""
import argparse
import os
import shutil
import sys

import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}
TASK_ROOT = os.path.dirname(os.path.abspath(__file__))
INITIAL_WORKSPACE = os.path.join(TASK_ROOT, "..", "initial_workspace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    # Clear email schema (FK order)
    for table in ["sent_log", "messages", "folders"]:
        try:
            cur.execute(f'DELETE FROM email."{table}"')
        except Exception:
            conn.rollback()
    conn.commit()

    # Insert a default inbox folder so email sending works
    cur.execute("INSERT INTO email.folders (name, flags) VALUES ('INBOX', '[\"\\\\HasNoChildren\"]') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO email.folders (name, flags) VALUES ('Sent', '[\"\\\\HasNoChildren\"]') ON CONFLICT DO NOTHING")
    conn.commit()

    cur.close()
    conn.close()
    print("Email schema cleared and default folders created.")

    # Copy initial_workspace files to agent_workspace
    if args.agent_workspace:
        initial_ws = os.path.abspath(INITIAL_WORKSPACE)
        agent_ws = args.agent_workspace
        os.makedirs(agent_ws, exist_ok=True)
        if os.path.exists(initial_ws):
            for fname in os.listdir(initial_ws):
                src = os.path.join(initial_ws, fname)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(agent_ws, fname))
            print(f"Copied initial workspace files to {agent_ws}")

    print("Preprocess complete.")


if __name__ == "__main__":
    main()
