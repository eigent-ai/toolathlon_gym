"""Preprocess: clear Google Sheet data for clean state."""
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
    cur.execute('DELETE FROM gsheet.cells')
    cur.execute('DELETE FROM gsheet.sheets')
    cur.execute('DELETE FROM gsheet.permissions')
    cur.execute('DELETE FROM gsheet.spreadsheets')
    cur.execute('DELETE FROM gsheet.folders')
    conn.commit()
    cur.close()
    conn.close()
    print("Google Sheet schema cleared.")


if __name__ == "__main__":
    main()
