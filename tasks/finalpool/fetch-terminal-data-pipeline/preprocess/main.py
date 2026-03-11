"""
Preprocess for fetch-terminal-data-pipeline task.

1. Clears gsheet schema.
"""

import os
import argparse
import asyncio

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def clear_gsheet(conn):
    """Clear all Google Sheet data."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
    conn.commit()
    print("[preprocess] Cleared gsheet schema.")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    # Clear Google Sheets schema
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        clear_gsheet(conn)
    finally:
        conn.close()

    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
