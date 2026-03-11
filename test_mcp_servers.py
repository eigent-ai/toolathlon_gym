"""
Test each MCP server by:
1. Resolving yaml config template variables
2. Starting server subprocess (stdio JSON-RPC)
3. Sending initialize + tools/list
4. Calling one lightweight tool per server
5. Reporting results

Usage:
    python test_mcp_servers.py                    # test all servers
    python test_mcp_servers.py word snowflake     # test specific servers
    python test_mcp_servers.py --list-tools       # only list tools, no calls
"""
import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_CONFIGS_DIR = SCRIPT_DIR / "configs" / "mcp_servers"
MCP_SERVERS_DIR = SCRIPT_DIR / "local_servers"
WORKSPACE_BASE = SCRIPT_DIR / "_test_workspace"

# ── Token placeholder values (PG-backed servers don't need real tokens) ───────
TOKEN_VARS = {
    "token.snowflake_account":            "local_pg",
    "token.snowflake_warehouse":          "local",
    "token.snowflake_user":               "postgres",
    "token.snowflake_private_key_path":   "",
    "token.snowflake_role":               "PUBLIC",
    "token.snowflake_database":           "toolathlon",
    "token.snowflake_schema":             "sf",
    "token.snowflake_op_allowed_databases": "toolathlon",
    "token.google_oauth2_credentials_path": "",
    "token.google_oauth2_token_path":     "",
    "token.google_sheets_folder_id":      "",
    "token.emails_config_file":           "",
    "token.notion_allowed_page_ids":      "",
    "token.notion_integration_key_eval":  "ntn-placeholder",
    "token.canvas_api_token":             "placeholder",
    "token.canvas_domain":                "localhost:8080",
    "token.google_client_id":             "placeholder",
    "token.google_client_secret":         "placeholder",
    "token.google_refresh_token":         "placeholder",
    "token.woocommerce_site_url":         "http://localhost:8081",
    "token.woocommerce_api_key":          "placeholder",
    "token.woocommerce_api_secret":       "placeholder",
}

# ── One representative read-only tool call per server ─────────────────────────
# Format: server_name -> (tool_name, arguments_dict)
SMOKE_CALLS = {
    "arxiv_local":          ("search_papers",        {"query": "transformer", "max_results": 1}),
    "arxiv-latex":          ("fetch_arxiv_latex",    {"arxiv_id": "1706.03762"}),
    "canvas":               ("list_courses",          {}),
    "emails":               ("list_folders",          {}),
    "excel":                ("list_sheets",           {"filepath": "nonexistent.xlsx"}),
    "filesystem":           ("list_directory",        {"path": "."}),
    "google_calendar":      ("list_events",           {"calendar_id": "primary", "max_results": 1}),
    "google_forms":         ("list_forms",            {}),
    "google_sheet":         ("list_spreadsheets",     {}),
    "howtocook":            ("getAllRecipes",          {}),
    "memory":               ("read_graph",            {}),
    "notion":               ("API-get-users",         {}),
    "fetch":                ("fetch",                 {"url": "https://example.com", "max_length": 500}),
    "pdf-tools":            ("list_pdf_files",        {"directory": "."}),
    "playwright_with_chunk":("browser_close",         {}),
    "pptx":                 ("list_presentations",    {"directory": "."}),
    "scholarly":            ("search_google_scholar", {"query": "deep learning", "num_results": 1}),
    "snowflake":            ("list_databases",        {}),
    "terminal":             ("run_command",           {"command": "echo hello"}),
    "woocommerce":          ("list_products",         {"per_page": 1}),
    "word":                 ("list_documents",        {"directory": "."}),
    "yahoo-finance":        ("get_stock_info",        {"symbol": "AAPL"}),
    "youtube":              ("search_videos",         {"query": "test", "max_results": 1}),
    "youtube_transcript":   ("get_transcript",        {"video_id": "dQw4w9WgXcQ"}),
    "rail_12306":           ("query_stations",        {}),
}

# ── JSON-RPC helpers ──────────────────────────────────────────────────────────
def make_request(method, params=None, req_id=1):
    msg = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        msg["params"] = params
    return (json.dumps(msg) + "\n").encode()

def parse_response(line: bytes):
    try:
        return json.loads(line.decode())
    except Exception:
        return None

# ── Template variable resolution ──────────────────────────────────────────────
def resolve(value, workspace: Path):
    if not isinstance(value, str):
        return value
    value = value.replace("${local_servers_paths}", str(MCP_SERVERS_DIR))
    value = value.replace("${agent_workspace}", str(workspace))
    for k, v in TOKEN_VARS.items():
        value = value.replace("${" + k + "}", v)
    return value

def resolve_list(lst, workspace):
    return [resolve(v, workspace) for v in lst]

def resolve_dict(d, workspace):
    return {k: resolve(v, workspace) for k, v in d.items()}

def load_yaml_config(yaml_path: Path, workspace: Path):
    with open(yaml_path) as f:
        cfg = yaml.safe_load(f)
    params = cfg.get("params", {})
    cmd = resolve(params.get("command", ""), workspace)
    args = resolve_list(params.get("args", []), workspace)
    env = resolve_dict(params.get("env", {}), workspace)
    cwd = resolve(params.get("cwd", str(workspace)), workspace)
    timeout = cfg.get("client_session_timeout_seconds", 30)
    name = cfg.get("name", yaml_path.stem)
    return {
        "name": name,
        "yaml_name": yaml_path.stem,
        "cmd": cmd,
        "args": args,
        "env": env,
        "cwd": cwd,
        "timeout": min(timeout, 30),
    }

# ── MCP server tester ─────────────────────────────────────────────────────────
class MCPTester:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.proc = None

    def start(self):
        full_env = {**os.environ, **self.cfg["env"]}
        cwd = self.cfg["cwd"]
        os.makedirs(cwd, exist_ok=True)
        self.proc = subprocess.Popen(
            [self.cfg["cmd"]] + self.cfg["args"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
            cwd=cwd,
        )

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except Exception:
                self.proc.kill()
            self.proc = None

    def send_recv(self, method, params=None, req_id=1, timeout=10):
        req = make_request(method, params, req_id)
        self.proc.stdin.write(req)
        self.proc.stdin.flush()
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self.proc.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue
            resp = parse_response(line)
            if resp and resp.get("id") == req_id:
                return resp
        return None

    def initialize(self):
        resp = self.send_recv("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"},
        }, req_id=0, timeout=15)
        if resp and "result" in resp:
            # send initialized notification
            notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
            self.proc.stdin.write(notif.encode())
            self.proc.stdin.flush()
            return True
        return False

    def list_tools(self):
        resp = self.send_recv("tools/list", {}, req_id=1, timeout=15)
        if resp and "result" in resp:
            return [t["name"] for t in resp["result"].get("tools", [])]
        return None

    def call_tool(self, tool_name, arguments):
        resp = self.send_recv("tools/call", {
            "name": tool_name,
            "arguments": arguments,
        }, req_id=2, timeout=20)
        if resp is None:
            return None, "timeout"
        if "error" in resp:
            return None, resp["error"].get("message", str(resp["error"]))
        return resp.get("result"), None


def test_server(yaml_path: Path, workspace: Path, list_only: bool, smoke_calls: dict):
    try:
        cfg = load_yaml_config(yaml_path, workspace)
    except Exception as e:
        return {"status": "CONFIG_ERROR", "error": str(e), "tools": []}

    tester = MCPTester(cfg)
    result = {"status": "UNKNOWN", "tools": [], "smoke": None, "error": None}

    try:
        tester.start()
        time.sleep(1.5)  # let server boot

        if not tester.initialize():
            result["status"] = "INIT_FAIL"
            stderr = tester.proc.stderr.read(500).decode(errors="replace")
            result["error"] = f"initialize failed. stderr: {stderr[:300]}"
            return result

        tools = tester.list_tools()
        if tools is None:
            result["status"] = "LIST_FAIL"
            return result

        result["tools"] = tools
        result["tool_count"] = len(tools)

        if list_only or not tools:
            result["status"] = "OK_LIST"
            return result

        # Smoke call
        server_name = cfg["name"]
        if server_name in smoke_calls:
            tool_name, arguments = smoke_calls[server_name]
            if tool_name in tools:
                res, err = tester.call_tool(tool_name, arguments)
                if err:
                    result["smoke"] = f"FAIL ({tool_name}): {err[:200]}"
                    result["status"] = "SMOKE_FAIL"
                else:
                    result["smoke"] = f"OK ({tool_name})"
                    result["status"] = "OK"
            else:
                # Try first tool with empty args
                first_tool = tools[0]
                res, err = tester.call_tool(first_tool, {})
                if err:
                    result["smoke"] = f"SKIP_CALL (smoke tool not found); tried {first_tool}: {err[:150]}"
                    result["status"] = "OK_LIST"
                else:
                    result["smoke"] = f"OK_FALLBACK ({first_tool})"
                    result["status"] = "OK"
        else:
            result["smoke"] = "no smoke call defined"
            result["status"] = "OK_LIST"

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
    finally:
        tester.stop()

    return result


def print_result(yaml_name, res):
    status = res["status"]
    color = {
        "OK":           "\033[92m",   # green
        "OK_LIST":      "\033[96m",   # cyan
        "SMOKE_FAIL":   "\033[93m",   # yellow
        "INIT_FAIL":    "\033[91m",   # red
        "LIST_FAIL":    "\033[91m",
        "CONFIG_ERROR": "\033[91m",
        "ERROR":        "\033[91m",
    }.get(status, "\033[0m")
    reset = "\033[0m"

    tool_count = res.get("tool_count", len(res.get("tools", [])))
    print(f"  {color}[{status}]{reset} {yaml_name:<30} tools={tool_count}", end="")
    if res.get("smoke"):
        print(f"  smoke={res['smoke']}", end="")
    if res.get("error"):
        print(f"  err={res['error'][:120]}", end="")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("servers", nargs="*", help="yaml stem names to test (default: all)")
    parser.add_argument("--list-tools", action="store_true", help="only list tools, skip smoke calls")
    parser.add_argument("--verbose", action="store_true", help="print all tool names")
    args = parser.parse_args()

    yaml_files = sorted(MCP_CONFIGS_DIR.glob("*.yaml"))
    if args.servers:
        yaml_files = [f for f in yaml_files if f.stem in args.servers]
        if not yaml_files:
            print(f"No yaml files matched: {args.servers}")
            sys.exit(1)

    print(f"\nTesting {len(yaml_files)} MCP server(s)...")
    print(f"  mcp_servers: {MCP_SERVERS_DIR}")
    print(f"  workspace:   {WORKSPACE_BASE}\n")

    results = {}
    for yaml_path in yaml_files:
        workspace = WORKSPACE_BASE / yaml_path.stem
        workspace.mkdir(parents=True, exist_ok=True)
        print(f"  Testing {yaml_path.stem}...", flush=True)
        res = test_server(yaml_path, workspace, args.list_tools, SMOKE_CALLS)
        results[yaml_path.stem] = res
        print(f"\033[1A\033[2K", end="")  # clear line
        print_result(yaml_path.stem, res)
        if args.verbose and res.get("tools"):
            for t in res["tools"]:
                print(f"      - {t}")

    # Summary
    ok = sum(1 for r in results.values() if r["status"] in ("OK", "OK_LIST"))
    fail = len(results) - ok
    print(f"\n{'='*60}")
    print(f"  Results: {ok}/{len(results)} passed, {fail} failed")
    if fail:
        print("  Failed:")
        for name, r in results.items():
            if r["status"] not in ("OK", "OK_LIST"):
                print(f"    - {name}: {r['status']} {r.get('error','')[:100]}")
    print(f"{'='*60}\n")

    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
