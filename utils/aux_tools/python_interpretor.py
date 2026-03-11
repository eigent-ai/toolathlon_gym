"""python_execute local tool for CAMEL."""
import os
import subprocess
import time
import uuid


def make_python_execute(agent_workspace: str):
    """Return a python_execute callable bound to agent_workspace."""

    async def python_execute(code: str, filename: str = "", timeout: int = 30) -> str:
        """Execute Python code in the agent workspace and return stdout/stderr.

        Args:
            code: Python source code to execute.
            filename: Optional filename (with .py). A random UUID name is used if omitted.
            timeout: Max execution time in seconds (capped at 120).
        """
        timeout = min(int(timeout), 120)
        if not filename:
            filename = f"{uuid.uuid4()}.py"
        if not filename.endswith(".py"):
            filename += ".py"

        workspace = os.path.abspath(agent_workspace)
        tmp_dir = os.path.join(workspace, ".python_tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        file_path = os.path.join(tmp_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        cmd = f"uv run --directory {workspace} ./.python_tmp/{filename}"
        start = time.time()
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True,
                text=True, encoding="utf-8", timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return f"=== TIMEOUT ===\nExceeded {timeout}s limit."

        elapsed = time.time() - start
        parts = []
        if result.stdout:
            parts += ["=== STDOUT ===", result.stdout.rstrip()]
        if result.stderr:
            parts += ["=== STDERR ===", result.stderr.rstrip()]
        parts += [
            "=== INFO ===",
            f"Return code: {result.returncode}",
            f"Time: {elapsed:.2f}s / {timeout}s limit",
        ]
        return "\n".join(parts) if parts else "No output."

    return python_execute
