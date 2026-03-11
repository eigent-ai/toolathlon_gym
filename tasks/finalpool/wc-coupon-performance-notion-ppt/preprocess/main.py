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

    # Clear notion schema
    cur.execute('DELETE FROM "notion"."blocks"')
    cur.execute('DELETE FROM "notion"."comments"')
    cur.execute('DELETE FROM "notion"."pages"')
    cur.execute('DELETE FROM "notion"."databases"')

    # Clear email schema
    cur.execute('DELETE FROM "email"."sent_log"')
    cur.execute('DELETE FROM "email"."messages"')

    conn.commit()
    cur.close()
    conn.close()
    print("Data cleared for schemas: notion, email")


if __name__ == "__main__":
    main()
