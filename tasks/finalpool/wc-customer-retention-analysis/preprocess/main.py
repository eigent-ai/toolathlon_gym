"""
Preprocess script for wc-customer-retention-analysis task.

1. Clears email and gsheet data (writable schemas).
2. Injects empty email folders.
3. Extracts mock_pages.tar.gz and starts HTTP server on port 30206.
4. WC schema is read-only -- do NOT modify.
"""

import argparse
import asyncio
import os
import shutil
import tarfile

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def clear_emails(cur):
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    cur.execute("DELETE FROM email.folders")
    print("[preprocess] Email data cleared.")


def clear_gsheet(cur):
    print("[preprocess] Clearing Google Sheet data...")
    for table in ["cells", "sheets", "spreadsheets", "permissions", "folders"]:
        cur.execute(f'DELETE FROM gsheet."{table}"')
    print("[preprocess] Google Sheet data cleared.")


def inject_email_folders(cur):
    print("[preprocess] Injecting email folders...")
    folders = [
        ("INBOX", "/"),
        ("Sent", "/"),
        ("Drafts", "/"),
    ]
    for name, delim in folders:
        cur.execute(
            "INSERT INTO email.folders (name, delimiter) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            (name, delim))
    print("[preprocess] Email folders injected.")


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30206."""
    print("[preprocess] Setting up mock benchmarks API...")

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
    print(f"[preprocess] Mock benchmarks API running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        clear_emails(cur)
        clear_gsheet(cur)
        inject_email_folders(cur)
        conn.commit()
        print("[preprocess] DB operations committed.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    await setup_mock_server()

    if args.agent_workspace:
        for fname in ["Customer_Retention.xlsx"]:
            fpath = os.path.join(args.agent_workspace, fname)
            if os.path.exists(fpath):
                os.remove(fpath)
                print(f"[preprocess] Removed {fpath}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
