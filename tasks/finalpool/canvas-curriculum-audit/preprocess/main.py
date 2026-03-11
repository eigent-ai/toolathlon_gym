"""
Preprocess script for canvas-curriculum-audit task.
Starts mock HTTP server on port 30217.
Canvas is read-only.
"""
import argparse
import asyncio
import os

PORT = 30217


async def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    # Start mock HTTP server
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    serve_dir = os.path.join(task_root, "tmp", "mock_pages")

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{PORT}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {PORT} --directory {serve_dir} "
        f"> {serve_dir}/server.log 2>&1 &"
    )
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server running at http://localhost:{PORT}")
    print("[preprocess] Done.")


if __name__ == "__main__":
    asyncio.run(main())
