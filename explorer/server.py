"""
Toolathlon-GYM Task Explorer — FastAPI backend
Run: uvicorn server:app --reload --port 8765
"""
import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).parent.parent
TASK_DIR = BASE / "tasks" / "finalpool"

app = FastAPI(title="Toolathlon-GYM Explorer")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── helpers ──────────────────────────────────────────────────────────────────

def _load_tasks():
    tasks = []
    for task_name in sorted(TASK_DIR.iterdir()):
        cfg_path = task_name / "task_config.json"
        if not cfg_path.exists():
            continue
        cfg = json.loads(cfg_path.read_text())
        mcps = cfg.get("needed_mcp_servers", [])

        def list_files(sub):
            d = task_name / sub
            if not d.is_dir():
                return []
            return sorted(
                str(p.relative_to(d))
                for p in d.rglob("*")
                if p.is_file() and p.name != ".gitkeep"
            )

        tasks.append({
            "name": task_name.name,
            "mcps": mcps,
            "mcp_count": len(mcps),
            "initial_files": list_files("initial_workspace"),
            "groundtruth_files": list_files("groundtruth_workspace"),
        })
    return tasks


TASKS = _load_tasks()
TASK_MAP = {t["name"]: t for t in TASKS}


# ── routes ───────────────────────────────────────────────────────────────────

@app.get("/api/tasks")
def get_tasks(
    mcp: Optional[str] = Query(None, description="Filter by MCP name"),
    q: Optional[str] = Query(None, description="Search task name"),
    mcp_count: Optional[int] = Query(None, description="Filter by number of MCPs"),
):
    result = TASKS
    if mcp:
        result = [t for t in result if mcp in t["mcps"]]
    if mcp_count is not None:
        result = [t for t in result if t["mcp_count"] == mcp_count]
    if q:
        q_lower = q.lower()
        result = [t for t in result if q_lower in t["name"].lower()]
    return result


@app.get("/api/tasks/{task_name}")
def get_task(task_name: str):
    if task_name not in TASK_MAP:
        raise HTTPException(404, "Task not found")
    t = TASK_MAP[task_name].copy()

    task_path = TASK_DIR / task_name

    # Read task description
    task_md = task_path / "docs" / "task.md"
    t["task_md"] = task_md.read_text() if task_md.exists() else ""

    # Read system prompt
    sys_prompt = task_path / "docs" / "agent_system_prompt.md"
    t["system_prompt"] = sys_prompt.read_text() if sys_prompt.exists() else ""

    return t


@app.get("/api/tasks/{task_name}/file")
def get_file(task_name: str, path: str = Query(...), workspace: str = Query("initial")):
    """Return raw text content of a text-based file."""
    if task_name not in TASK_MAP:
        raise HTTPException(404, "Task not found")
    if workspace == "initial":
        base = TASK_DIR / task_name / "initial_workspace"
    elif workspace == "groundtruth":
        base = TASK_DIR / task_name / "groundtruth_workspace"
    else:
        raise HTTPException(400, "workspace must be 'initial' or 'groundtruth'")

    full = (base / path).resolve()
    if not str(full).startswith(str(base.resolve())):
        raise HTTPException(403, "Forbidden")
    if not full.exists():
        raise HTTPException(404, "File not found")

    TEXT_EXTS = {".md", ".txt", ".json", ".py", ".csv", ".bib", ".yaml", ".yml", ".toml"}
    if full.suffix.lower() in TEXT_EXTS:
        return {"type": "text", "content": full.read_text(errors="replace")}
    return {"type": "binary", "content": f"[Binary file: {full.name}]"}


@app.get("/api/stats")
def get_stats():
    from collections import Counter
    mcp_usage = Counter()
    mcp_dist = Counter()
    for t in TASKS:
        mcp_dist[t["mcp_count"]] += 1
        for m in t["mcps"]:
            mcp_usage[m] += 1

    ext_counter = Counter()
    for t in TASKS:
        for f in t["initial_files"]:
            ext = Path(f).suffix.lower()
            if ext:
                ext_counter[ext] += 1

    return {
        "total_tasks": len(TASKS),
        "mcp_distribution": dict(sorted(mcp_dist.items())),
        "mcp_usage": dict(mcp_usage.most_common()),
        "initial_file_types": dict(ext_counter.most_common()),
        "db_schemas": {
            "canvas": {"rows": 311341, "description": "Canvas LMS — 22 courses, 28,865 users, 32,663 enrollments, 173,912 submissions"},
            "sf_data": {"rows": 139044, "description": "Snowflake DW — 50,000 employees, 20,000 sales orders, 31,588 support tickets"},
            "wc": {"rows": 1146, "description": "WooCommerce — 82 products, 150 orders, 50 customers, 396 reviews"},
            "yf": {"rows": 3856, "description": "Yahoo Finance — 50 tickers, 3,510 price records"},
            "youtube": {"rows": 148, "description": "YouTube — 3 channels, 2 playlists, 135 videos"},
            "train": {"rows": 79, "description": "12306 Rail — 8 trains, 16 routes"},
            "notion": {"rows": 11, "description": "Notion (writable placeholder)"},
            "email": {"rows": 8, "description": "Email (writable placeholder)"},
            "arxiv": {"rows": 7, "description": "ArXiv (writable placeholder)"},
            "scholarly": {"rows": 5, "description": "Scholarly (writable placeholder)"},
            "gform": {"rows": 4, "description": "Google Forms (writable placeholder)"},
        },
    }


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = Path(__file__).parent / "index.html"
    return html_path.read_text()
