"""
Preprocess for howtocook-nutrition-benchmark task.
- Starts mock HTTP server on port 30232 for nutrition benchmarks.
- No database injection needed (howtocook uses MCP, not DB).
"""
import argparse
import asyncio
import os
import shutil
import tarfile


MOCK_PORT = 30232


async def setup_mock_server():
    task_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_dir = os.path.join(task_root, "files")
    tmp_dir = os.path.join(task_root, "tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir, exist_ok=True)

    tar_path = os.path.join(files_dir, "mock_pages.tar.gz")
    mock_src = os.path.join(files_dir, "mock_pages")
    if not os.path.exists(tar_path) and os.path.exists(mock_src):
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(mock_src, arcname="mock_pages")

    if os.path.exists(tar_path):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)
        serve_dir = os.path.join(tmp_dir, "mock_pages")
    else:
        serve_dir = tmp_dir
        if os.path.exists(mock_src):
            shutil.copytree(mock_src, os.path.join(tmp_dir, "mock_pages"))
            serve_dir = os.path.join(tmp_dir, "mock_pages")

    kill_proc = await asyncio.create_subprocess_shell(
        f"kill -9 $(lsof -ti:{MOCK_PORT}) 2>/dev/null",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await kill_proc.wait()
    await asyncio.sleep(0.5)

    await asyncio.create_subprocess_shell(
        f"nohup python3 -m http.server {MOCK_PORT} --directory {serve_dir} "
        f"> {serve_dir}/server.log 2>&1 &")
    await asyncio.sleep(1)
    print(f"[preprocess] Mock server at http://localhost:{MOCK_PORT}")


async def main():
    # No writable schemas to DELETE - read-only data sources
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", type=str, required=False)
    parser.add_argument("--launch_time", type=str, required=False)
    args = parser.parse_args()

    await setup_mock_server()
    print("[preprocess] Preprocessing completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
