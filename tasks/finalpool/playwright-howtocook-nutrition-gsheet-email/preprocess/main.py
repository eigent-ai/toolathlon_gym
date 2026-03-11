"""
Preprocess script for playwright-howtocook-nutrition-gsheet-email task.

This script:
1. Clears Google Sheets, email data
2. Injects noise data into gsheet and email
3. Extracts mock_pages.tar.gz and starts HTTP server on port 30206
"""

import argparse
import asyncio
import json
import os
import shutil
import tarfile
import uuid

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_gsheet(cur):
    """Clear all Google Sheets data."""
    print("[preprocess] Clearing Google Sheets data...")
    cur.execute("DELETE FROM gsheet.cells")
    cur.execute("DELETE FROM gsheet.permissions")
    cur.execute("DELETE FROM gsheet.sheets")
    cur.execute("DELETE FROM gsheet.spreadsheets")
    print("[preprocess] Google Sheets data cleared.")


def clear_emails(cur):
    """Clear all email data."""
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    try:
        cur.execute("DELETE FROM email.sent_log")
    except Exception:
        pass
    cur.execute("DELETE FROM email.messages")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    print("[preprocess] Email data cleared.")


def inject_noise_gsheet(cur):
    """Inject noise spreadsheet data."""
    print("[preprocess] Injecting noise Google Sheets data...")
    noise_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s)",
        (noise_id, "Q4_Budget_Tracking"),
    )
    # sheets.id is auto-increment integer, so let DB assign it
    cur.execute(
        "INSERT INTO gsheet.sheets (spreadsheet_id, title, \"index\", row_count, column_count) "
        "VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (noise_id, "Budget", 0, 10, 5),
    )
    sheet_id = cur.fetchone()[0]
    # Insert a noise cell
    cur.execute(
        "INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value) "
        "VALUES (%s, %s, %s, %s, %s)",
        (noise_id, sheet_id, 0, 0, "Department"),
    )
    print("[preprocess] Noise Google Sheets data injected.")


def inject_noise_email(cur):
    """Inject noise email data."""
    print("[preprocess] Injecting noise email data...")
    cur.execute("SELECT id FROM email.folders WHERE name = 'INBOX' LIMIT 1")
    row = cur.fetchone()
    if not row:
        return
    folder_id = row[0]
    cur.execute(
        """INSERT INTO email.messages
            (folder_id, message_id, subject, from_addr, to_addr, body_text)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            folder_id,
            f"<noise-{uuid.uuid4()}@company.com>",
            "Q4 Budget Review Meeting",
            "finance@company.com",
            json.dumps(["team@company.com"]),
            "Please review the attached Q4 budget report before Friday.",
        ),
    )
    print("[preprocess] Noise email data injected.")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30206."""
    print("[preprocess] Setting up mock nutrition guidelines server...")

    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)
    print(f"[preprocess] Extracted {tar_path} to {tmp_dir}")

    mock_dir = os.path.join(tmp_dir, "mock_pages")
    port = 30206

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
    print(f"[preprocess] Mock server running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_gsheet(cur)
        clear_emails(cur)
        inject_noise_gsheet(cur)
        inject_noise_email(cur)
        conn.commit()
        print("[preprocess] Database operations committed.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Database error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    await setup_mock_server()
    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
