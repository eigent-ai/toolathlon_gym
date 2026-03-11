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

    # Clear gsheet schema
    cur.execute('DELETE FROM "gsheet"."cells"')
    cur.execute('DELETE FROM "gsheet"."sheets"')
    cur.execute('DELETE FROM "gsheet"."permissions"')
    cur.execute('DELETE FROM "gsheet"."spreadsheets"')
    cur.execute('DELETE FROM "gsheet"."folders"')

    # Clear email schema (sent messages)
    cur.execute('DELETE FROM "email"."sent_log"')
    cur.execute('DELETE FROM "email"."messages"')

    # Clear notion schema
    cur.execute('DELETE FROM "notion"."blocks"')
    cur.execute('DELETE FROM "notion"."comments"')
    cur.execute('DELETE FROM "notion"."pages"')
    cur.execute('DELETE FROM "notion"."databases"')

    conn.commit()
    cur.close()
    conn.close()
    print("Data cleared for schemas: gsheet, email, notion")


if __name__ == "__main__":
    main()
