"""
Preprocess script for support-sla-audit-form task.

This script:
1. Clears Google Forms data (responses -> questions -> forms) in the gform schema
2. Extracts mock_pages.tar.gz and starts an HTTP server on port 30162
3. Does NOT touch Snowflake data (read-only)
"""

import argparse
import os
import shutil
import subprocess
import tarfile
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": "toolathlon_gym",
    "user": "eigent",
    "password": "camel",
}


def clear_gform(cur):
    """Clear all Google Forms data."""
    print("[preprocess] Clearing Google Forms data...")
    cur.execute("DELETE FROM gform.responses")
    cur.execute("DELETE FROM gform.questions")
    cur.execute("DELETE FROM gform.forms")
    print("[preprocess] Google Forms data cleared.")


def setup_mock_server():
    """Extract mock pages and start HTTP server on port 30162."""
    task_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_dir, "files")
    tmp_dir = os.path.join(task_dir, "tmp")

    # Clean and recreate tmp directory
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    # Extract mock_pages.tar.gz
    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    if os.path.exists(tar_path):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)
        print(f"[preprocess] Extracted mock_pages.tar.gz to {tmp_dir}")
    else:
        print(f"[preprocess] WARNING: {tar_path} not found")
        return

    # The HTML files are in tmp/mock_pages/
    serve_dir = os.path.join(tmp_dir, "mock_pages")
    if not os.path.exists(serve_dir):
        serve_dir = tmp_dir

    # Kill any existing process on port 30162
    try:
        subprocess.run(
            "kill -9 $(lsof -ti:30162) 2>/dev/null",
            shell=True,
            capture_output=True,
        )
        print("[preprocess] Killed existing process on port 30162")
    except Exception:
        pass

    # Start HTTP server on port 30162
    log_file = os.path.join(tmp_dir, "http.log")
    cmd = f"nohup python -m http.server 30162 --directory {serve_dir} > {log_file} 2>&1 &"
    subprocess.Popen(cmd, shell=True)
    print(f"[preprocess] Started HTTP server on port 30162 serving {serve_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    # Step 1: Clear Google Forms data
    print("\n" + "=" * 60)
    print("STEP 1: Clear Google Forms Data")
    print("=" * 60)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        clear_gform(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error clearing gform: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # Step 2: Set up mock HTTP server
    print("\n" + "=" * 60)
    print("STEP 2: Set Up Mock HTTP Server")
    print("=" * 60)
    setup_mock_server()

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
