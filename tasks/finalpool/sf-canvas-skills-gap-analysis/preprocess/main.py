"""Preprocess for sf-canvas-skills-gap-analysis.
Clears email data and starts mock HTTP server for skills portal on port 30237.
SF and Canvas are read-only.
"""
import argparse
import asyncio
import os
import shutil

import psycopg2

DB = dict(
    host=os.environ.get("PGHOST", "localhost"),
    port=int(os.environ.get("PGPORT", "5432")),
    dbname=os.environ.get("PGDATABASE", "toolathlon_gym"),
    user=os.environ.get("PGUSER", "eigent"),
    password=os.environ.get("PGPASSWORD", "camel"),
)


def clear_email(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM email.attachments")
    try:
        cur.execute("DELETE FROM email.sent_log")
    except Exception:
        conn.rollback()
    cur.execute("DELETE FROM email.messages")
    conn.commit()
    cur.close()
    print("[preprocess] Email data cleared.")


async def setup_mock_server():
    """Start HTTP server on port 30237 serving skills portal pages."""
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files", "mock_pages")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    shutil.copytree(files_dir, tmp_dir)
    print(f"[preprocess] Copied mock_pages to {tmp_dir}")

    port = 30237
    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{port}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {port} --directory {tmp_dir} "
        f"> {tmp_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Skills portal running at http://localhost:{port}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB)
    clear_email(conn)
    conn.close()

    await setup_mock_server()

    if args.agent_workspace:
        initial_ws = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "initial_workspace"
        )
        for f in os.listdir(initial_ws):
            src = os.path.join(initial_ws, f)
            if os.path.isfile(src) and not f.startswith("."):
                shutil.copy2(src, os.path.join(args.agent_workspace, f))
        print(f"[preprocess] Copied initial_workspace files to {args.agent_workspace}")

    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
