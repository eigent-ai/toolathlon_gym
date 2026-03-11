"""
Build CAMEL MCPClient objects from yaml configs.
"""
import os
import yaml
from pathlib import Path
from typing import List

from camel.utils.mcp_client import MCPClient, ServerConfig


def _resolve(value, local_servers_path: str, agent_workspace: str) -> str:
    if not isinstance(value, str):
        return value
    return (value
            .replace("${local_servers_paths}", local_servers_path)
            .replace("${agent_workspace}", agent_workspace))


def build_mcp_clients(
    needed_servers: List[str],
    agent_workspace: str,
    config_dir: str = "configs/mcp_servers",
) -> List[MCPClient]:
    """Build MCPClient list from yaml configs for the requested servers."""
    local_servers_path = os.environ.get("LOCAL_SERVERS_PATH", os.path.abspath("./local_servers"))
    agent_workspace = os.path.abspath(agent_workspace)

    clients: List[MCPClient] = []
    config_path = Path(config_dir)
    if not config_path.exists():
        raise FileNotFoundError(f"MCP config dir not found: {config_dir}")

    for config_file in sorted(config_path.glob("*.yaml")):
        with open(config_file, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        if not cfg:
            continue
        name = cfg.get("name", config_file.stem)
        if name not in needed_servers:
            continue

        params = cfg.get("params", {})
        resolve = lambda v: _resolve(v, local_servers_path, agent_workspace)

        command = resolve(params.get("command", ""))
        args = [resolve(a) for a in params.get("args", [])]
        env = {k: resolve(v) for k, v in params.get("env", {}).items()}
        cwd = resolve(params.get("cwd", agent_workspace))

        # Merge with current process environment so servers inherit PATH etc.
        full_env = {**os.environ, **env}
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
    missing = [s for s in needed_servers if s not in found]
    if missing:
        print(f"[tool_servers] Warning: no yaml config found for: {missing}")

    return clients
