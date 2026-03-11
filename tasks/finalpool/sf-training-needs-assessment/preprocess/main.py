"""
Preprocess script for sf-training-needs-assessment task.

1. Clears email data.
2. Extracts mock_pages.tar.gz and starts HTTP server on port 30214.
3. Snowflake HR data is read-only.
"""
import argparse
import glob as globmod
import os
import shutil
import subprocess
import tarfile

import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}

PORT = 30214


def clear_email(cur):
    print("[preprocess] Clearing email data...")
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages WHERE folder_id != 0")
    try:
        cur.execute("DELETE FROM email.drafts")
    except Exception:
        pass
    print("[preprocess] Email data cleared.")


def setup_mock_server():
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    if os.path.exists(tar_path):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)
        print(f"[preprocess] Extracted mock_pages.tar.gz to {tmp_dir}")
    else:
        print(f"[preprocess] WARNING: {tar_path} not found")
        return

    serve_dir = os.path.join(tmp_dir, "mock_pages")
    if not os.path.exists(serve_dir):
        serve_dir = tmp_dir

    try:
        subprocess.run(
            f"kill -9 $(lsof -ti:{PORT}) 2>/dev/null",
            shell=True, capture_output=True,
        )
    except Exception:
        pass

    log_file = os.path.join(tmp_dir, "http.log")
    cmd = f"nohup python3 -m http.server {PORT} --directory {serve_dir} > {log_file} 2>&1 &"
    subprocess.Popen(cmd, shell=True)
    print(f"[preprocess] Started HTTP server on port {PORT} serving {serve_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        clear_email(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    setup_mock_server()

    if args.agent_workspace:
        for pattern in ["Training_Needs.xlsx"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    main()
