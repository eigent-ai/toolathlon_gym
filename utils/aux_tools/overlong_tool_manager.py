"""
Overlong tool output manager for CAMEL.
Saves large tool outputs to disk; agent can search/view them by ID.
"""
import json
import os
import time
import uuid
from typing import Optional

OVERLONG_DIR = ".overlong_tool_outputs"
PAGE_SIZE = 10000  # chars per view page


def make_overlong_tools(agent_workspace: str):
    """Return (save_overlong, view_overlong) callables bound to workspace."""
    overlong_dir = os.path.join(os.path.abspath(agent_workspace), OVERLONG_DIR)

    def _dir():
        os.makedirs(overlong_dir, exist_ok=True)
        return overlong_dir

    async def save_overlong_output(content: str, label: str = "") -> str:
        """Save a large text to disk and return a reference ID.

        Args:
            content: The large text content to store.
            label: Optional human-readable label for this output.
        """
        fid = str(uuid.uuid4())[:8]
        path = os.path.join(_dir(), f"{fid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"id": fid, "label": label, "content": content,
                       "saved_at": time.time()}, f)
        preview = content[:200] + ("..." if len(content) > 200 else "")
        return (f"Saved {len(content)} chars as [{fid}] label='{label}'.\n"
                f"Preview: {preview}\n"
                f"Use view_overlong_output(id='{fid}') to read.")

    async def view_overlong_output(id: str, page: int = 0) -> str:
        """View a saved overlong output by ID, paginated.

        Args:
            id: The reference ID returned by save_overlong_output.
            page: Page number (0-indexed, each page ~10000 chars).
        """
        path = os.path.join(_dir(), f"{id}.json")
        if not os.path.exists(path):
            return f"No saved output with id '{id}'."
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        content = data["content"]
        total_pages = max(1, (len(content) + PAGE_SIZE - 1) // PAGE_SIZE)
        start = page * PAGE_SIZE
        chunk = content[start: start + PAGE_SIZE]
        return (f"[{id}] label='{data['label']}' | "
                f"page {page+1}/{total_pages} | "
                f"chars {start}–{start+len(chunk)} of {len(content)}\n\n"
                f"{chunk}")

    return save_overlong_output, view_overlong_output
