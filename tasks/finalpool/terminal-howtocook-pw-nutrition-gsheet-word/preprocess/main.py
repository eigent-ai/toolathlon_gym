"""Preprocess for terminal-howtocook-pw-nutrition-gsheet-word.
Clears gsheet writable schema. Extracts mock pages and starts HTTP server on port 30404."""
import argparse
import asyncio
import os
import glob as globmod
import shutil
import tarfile
import uuid
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"), "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent", "password": "camel",
}

TASK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def clear_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM gsheet.cells")
        cur.execute("DELETE FROM gsheet.sheets")
        cur.execute("DELETE FROM gsheet.spreadsheets")
        conn.commit()
        print("[preprocess] Cleared gsheet data.")

        # Inject gsheet noise
        ss_id = f"noise-{uuid.uuid4()}"
        cur.execute("INSERT INTO gsheet.spreadsheets (id, title) VALUES (%s, %s)", (ss_id, "Unrelated Budget Notes"))
        cur.execute("INSERT INTO gsheet.sheets (spreadsheet_id, title, index) VALUES (%s, %s, 0) RETURNING id", (ss_id, "Notes"))
        sh_id = cur.fetchone()[0]
        cur.execute("INSERT INTO gsheet.cells (spreadsheet_id, sheet_id, row_index, col_index, value) VALUES (%s, %s, 1, 1, 'Random budget notes')", (ss_id, sh_id))
        conn.commit()
        print("[preprocess] Injected noise data.")
    except Exception as e:
        conn.rollback()
        print(f"[preprocess] Error clearing gsheet: {e}")
        raise
    finally:
        cur.close()
        conn.close()


async def setup_mock_server():
    """Extract mock_pages.tar.gz and start HTTP server on port 30404."""
    files_dir = os.path.join(TASK_ROOT, "files")
    tmp_dir = os.path.join(TASK_ROOT, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=tmp_dir)
    print(f"[preprocess] Extracted {tar_path} to {tmp_dir}")

    mock_dir = os.path.join(tmp_dir, "task4_mock_pages")
    port = 30404

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{port}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {port} --directory {mock_dir} "
        f"> {mock_dir}/server.log 2>&1 &")
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    clear_db()
    await setup_mock_server()

    if args.agent_workspace:
        for pattern in ["Wellness_Diet_Plan.docx", "nutrition_calculator.py"]:
            for f in globmod.glob(os.path.join(args.agent_workspace, pattern)):
                os.remove(f)
                print(f"[preprocess] Removed {f}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
