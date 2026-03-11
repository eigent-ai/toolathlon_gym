"""Preprocess for yf-peer-comparison-excel-ppt-email. Clears email data and injects noise emails."""
import os
import argparse
import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        # Clear email tables
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")

        # Get inbox folder id
        cur.execute("SELECT id FROM email.folders WHERE LOWER(name) LIKE '%inbox%' LIMIT 1")
        row = cur.fetchone()
        inbox_fid = row[0] if row else 1

        # Inject noise emails
        cur.execute("""
            INSERT INTO email.messages (subject, from_addr, to_addr, body_text, folder_id)
            VALUES
            ('Weekly Market Digest - March 2026',
             'markets@newsletter.example.com',
             '["assistant@company.example.com"]',
             'This week saw mixed performance across major indices. Technology stocks continued their pullback while energy and healthcare sectors showed strength.',
             %s),
            ('Reminder: Q1 Earnings Call Schedule',
             'events@firm.com',
             '["assistant@company.example.com"]',
             'Please find attached the Q1 2026 earnings call schedule for our coverage universe. Key dates: AMZN April 24, GOOGL April 22, JNJ April 15, JPM April 11, XOM April 25.',
             %s),
            ('Office IT Maintenance Window',
             'it@firm.com',
             '["assistant@company.example.com"]',
             'Scheduled maintenance this Saturday from 2am to 6am. Email and calendar services may be briefly unavailable.',
             %s)
        """, (inbox_fid, inbox_fid, inbox_fid))

        conn.commit()
        print("[preprocess] Cleared email data and injected noise emails.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
