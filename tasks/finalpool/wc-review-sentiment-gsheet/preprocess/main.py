"""Preprocess: clear writable schema data for clean state."""
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

    # Clear Google Sheet tables (FK order)
    for table in ["cells", "sheets", "spreadsheets", "permissions", "folders"]:
        cur.execute(f'DELETE FROM gsheet."{table}"')

    conn.commit()
    cur.close()
    conn.close()
    print("Data cleared for schemas: gsheet")


if __name__ == "__main__":
    main()
