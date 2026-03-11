"""Preprocess for yf-portfolio-stress-test. Starts mock API server on port 30224."""
import argparse
import asyncio
import os
import shutil


PORT = 30224


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
    print(f"[preprocess] Mock API server running at http://localhost:{PORT}")


async def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    await setup_mock_server()
    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
