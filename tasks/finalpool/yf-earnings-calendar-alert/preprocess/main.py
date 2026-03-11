"""Preprocess for yf-earnings-calendar-alert.
Clears email schema and starts mock web server on port 30225."""
import argparse
import asyncio
import os
import shutil
import psycopg2

PORT = 30225
DB = dict(host=os.environ.get("PGHOST", "localhost"), port=5432, dbname="toolathlon_gym", user="eigent", password="camel")


def clear_email():
    conn = psycopg2.connect(**DB)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DELETE FROM email.attachments")
    cur.execute("DELETE FROM email.sent_log")
    cur.execute("DELETE FROM email.messages")
    # Ensure sent folder exists
    cur.execute("SELECT id FROM email.folders WHERE LOWER(name) LIKE '%sent%' LIMIT 1")
    if not cur.fetchone():
        cur.execute("INSERT INTO email.folders (name) VALUES ('Sent')")
    cur.close()
    conn.close()
    print("[preprocess] Cleared email tables.")


async def run_command(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await proc.wait()


async def setup_mock_server():
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_dir = os.path.join(task_root, "files", "mock_pages")
    tmp_dir = os.path.join(task_root, "tmp")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    await run_command(f"kill -9 $(lsof -ti:{PORT}) 2>/dev/null")
    await asyncio.sleep(0.5)
    log_path = os.path.join(tmp_dir, "server.log")
    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {PORT} --directory {mock_dir} > {log_path} 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server running at http://localhost:{PORT}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    clear_email()
    await setup_mock_server()
    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
