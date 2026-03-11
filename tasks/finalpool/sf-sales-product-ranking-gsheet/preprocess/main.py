"""Preprocess: clear gsheet data for clean evaluation state."""
import os
import argparse
import psycopg2

DB = {"host": os.environ.get("PGHOST", "localhost"), "port": 5432, "dbname": "toolathlon_gym", "user": "eigent", "password": "camel"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    for t in ["gsheet.cells", "gsheet.sheets", "gsheet.permissions", "gsheet.spreadsheets", "gsheet.folders"]:
        cur.execute(f"DELETE FROM {t}")
        print(f"[preprocess] Cleared {t}")

    conn.commit()
    cur.close()
    conn.close()
    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
