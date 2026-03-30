"""
Build CAMEL MCPClient objects from yaml configs or HTTP URLs.
"""
import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional

from camel.utils.mcp_client import MCPClient, ServerConfig


def _resolve(value, local_servers_path: str, agent_workspace: str, task_dir: str = "") -> str:
    if not isinstance(value, str):
        return value
    return (value
            .replace("${local_servers_paths}", local_servers_path)
            .replace("${agent_workspace}", agent_workspace)
            .replace("${task_dir}", task_dir))


def build_mcp_clients(
    needed_servers: List[str],
    agent_workspace: str,
    config_dir: str = "configs/mcp_servers",
    task_dir: str = "",
    http_mcp_urls: Optional[Dict[str, str]] = None,
    http_mcp_timeout: float = 600.0,
) -> List[MCPClient]:
    """Build MCPClient list from yaml configs for the requested servers.

    If http_mcp_urls is provided (dict of name->url), those servers will be
    connected via HTTP (streamable-http) instead of stdio.
    """
    local_servers_path = os.environ.get("LOCAL_SERVERS_PATH", os.path.abspath("./local_servers"))
    agent_workspace = os.path.abspath(agent_workspace)
    task_dir = os.path.abspath(task_dir) if task_dir else ""

    clients: List[MCPClient] = []
    remaining = list(needed_servers)

    # HTTP MCP servers (e.g., Harbor sidecar containers via streamable-http)
    if http_mcp_urls:
        for name, url in http_mcp_urls.items():
            if name not in remaining:
                continue
            server_config = ServerConfig(url=url, timeout=http_mcp_timeout)
            clients.append(MCPClient(config=server_config, timeout=http_mcp_timeout))
            remaining.remove(name)

    if not remaining:
        return clients

    config_path = Path(config_dir)
    if not config_path.exists():
        raise FileNotFoundError(f"MCP config dir not found: {config_dir}")

    for config_file in sorted(config_path.glob("*.yaml")):
        with open(config_file, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        if not cfg:
            continue
        name = cfg.get("name", config_file.stem)
        if name not in remaining:
            continue

        params = cfg.get("params", {})
        resolve = lambda v: _resolve(v, local_servers_path, agent_workspace, task_dir)

        command = resolve(params.get("command", ""))
        args = [resolve(a) for a in params.get("args", [])]
        env = {k: resolve(v) for k, v in params.get("env", {}).items()}
        cwd = resolve(params.get("cwd", agent_workspace))

        # Merge envs: process env takes priority over yaml defaults so that
        # runtime overrides (e.g. PG_HOST=localhost PG_PORT=5441 injected by
        # the Harbor runner) are not clobbered by yaml-level defaults.
        full_env = {**env, **os.environ}

        # Bridge standard libpq env vars (PGHOST/PGPORT/...) to the PG_* names
        # used by MCP servers (emails-mcp, woocommerce-mcp, yahoo-finance-mcp).
        # This ensures Harbor runner's PGHOST/PGPORT override yaml defaults.
        _pg_bridge = {
            "PG_HOST": full_env.get("PGHOST"),
            "PG_PORT": full_env.get("PGPORT"),
            "PG_DATABASE": full_env.get("PGDATABASE"),
            "PG_USER": full_env.get("PGUSER"),
            "PG_PASSWORD": full_env.get("PGPASSWORD"),
        }
        for k, v in _pg_bridge.items():
            if v is not None:
                full_env[k] = v
        os.makedirs(cwd, exist_ok=True)

        server_config = ServerConfig(
            command=command,
            args=args,
            env=full_env,
            cwd=cwd,
        )
        timeout = cfg.get("client_session_timeout_seconds", 60)
        clients.append(MCPClient(config=server_config, timeout=float(timeout)))

    found = {cfg.get("name", f.stem) for f in config_path.glob("*.yaml")
             for cfg in [yaml.safe_load(open(f))] if cfg}
    missing = [s for s in remaining if s not in found]
    if missing:
        print(f"[tool_servers] Warning: no yaml config found for: {missing}")

    return clients
