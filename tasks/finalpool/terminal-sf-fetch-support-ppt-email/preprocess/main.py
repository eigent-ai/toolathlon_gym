"""Preprocess for terminal-sf-fetch-support-ppt-email.
Clears email data, injects noise emails, starts mock CSAT benchmark server on port 30408.
Snowflake SUPPORT_CENTER is read-only.
"""
import argparse
import asyncio
import json
import os
import shutil
import tarfile
import uuid

import psycopg2

DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432,
          dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
          user="eigent", password="camel")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30408."""
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)

    mock_dir = os.path.join(tmp_dir, "mock_pages")
    port = 30408

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{port}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {port} --directory {mock_dir} "
        f"> {mock_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock CSAT benchmark server running at http://localhost:{port}")


def clear_and_inject_email():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")
        cur.execute("DELETE FROM email.drafts")
        conn.commit()
        print("[preprocess] Cleared email schema.")

        cur.execute("SELECT id FROM email.folders WHERE name='INBOX' LIMIT 1")
        inbox_id = cur.fetchone()[0]

        noise = [
            ("Q1 Support Budget Approved", "finance@company.example.com",
             json.dumps(["support@company.example.com"]),
             "The Q1 support budget has been approved. Please review the allocation."),
            ("New Knowledge Base Articles Published", "kb@company.example.com",
             json.dumps(["agents@company.example.com"]),
             "Five new knowledge base articles have been published this week."),
            ("Office Closure Next Friday", "hr@company.example.com",
             json.dumps(["all@company.example.com"]),
             "Reminder that the office will be closed next Friday for the holiday."),
        ]
        for subj, from_addr, to_addr, body in noise:
            cur.execute(
                "INSERT INTO email.messages (folder_id, message_id, subject, from_addr, to_addr, "
                "body_text, is_read, date) VALUES (%s, %s, %s, %s, %s, %s, false, now())",
                (inbox_id, f"noise-{uuid.uuid4()}@company.example.com", subj, from_addr, to_addr, body)
            )
        conn.commit()
        print("[preprocess] Injected 3 noise emails.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    clear_and_inject_email()
    await setup_mock_server()
    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
