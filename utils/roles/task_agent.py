"""TaskAgent using CAMEL ChatAgent."""
import asyncio, json, os, shutil, subprocess, traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.toolkits import FunctionTool, MCPToolkit

from utils.aux_tools.basic import make_claim_done, sleep
from utils.aux_tools.overlong_tool_manager import make_overlong_tools
from utils.aux_tools.python_interpretor import make_python_execute
from utils.data_structures.task_config import TaskConfig
from utils.general.helper import copy_folder_contents, print_color
from utils.mcp.tool_servers import build_mcp_clients


class TaskStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    MAX_TURNS_REACHED = "max_turns_reached"
    INTERRUPTED = "interrupted"


async def _noop(*args, **kwargs) -> str:
    """Stub for unsupported local tools (manage_context, history, etc.)."""
    return "OK"


def _fix_schema(schema: dict, strict_openai: bool = False):
    """Recursively fix tool parameter schemas for broad model compatibility.

    - Removes 'enum' from fields whose type is not 'string' (Gemini rejects these).
    - Adds 'type': 'string' to array items missing a type key (OpenAI rejects these).
    - When strict_openai=True, collapses oneOf/anyOf to a single type (OpenAI strict mode).
    """
    if not isinstance(schema, dict):
        return
    # Fix enum on non-string fields
    if "enum" in schema and schema.get("type", "string") != "string":
        del schema["enum"]
    # Fix array items missing type
    if schema.get("type") == "array" and "items" in schema:
        items = schema["items"]
        if isinstance(items, dict) and "type" not in items and not any(
            k in items for k in ("anyOf", "oneOf", "allOf", "$ref")
        ):
            items["type"] = "string"
        _fix_schema(items, strict_openai)
    # Recurse into properties and nested schemas
    for key in ("properties", "additionalProperties"):
        val = schema.get(key)
        if isinstance(val, dict):
            for v in val.values():
                _fix_schema(v, strict_openai)
    for key in ("allOf", "anyOf", "oneOf"):
        for sub in schema.get(key, []):
            _fix_schema(sub, strict_openai)


def _strip_strict_mode(schema: dict):
    """Recursively remove CAMEL-injected strict-mode markers (additionalProperties: false)
    and strip the top-level 'strict: true' so OpenAI uses non-strict mode."""
    if not isinstance(schema, dict):
        return
    # Remove additionalProperties: false (CAMEL adds this for strict mode)
    if schema.get("additionalProperties") is False:
        del schema["additionalProperties"]
    # Recurse
    for key in ("properties",):
        val = schema.get(key)
        if isinstance(val, dict):
            for v in val.values():
                _strip_strict_mode(v)
    for key in ("allOf", "anyOf", "oneOf"):
        for sub in schema.get(key, []):
            _strip_strict_mode(sub)
    if schema.get("type") == "array" and "items" in schema:
        _strip_strict_mode(schema["items"])


def _sanitize_tool_schemas(tools, max_output_chars: int = 8000, strict_openai: bool = False):
    """Patch openai_tool_schema in-place for all FunctionTools.
    Also wraps each tool's function to truncate long outputs."""
    for tool in tools:
        # Fix schemas
        try:
            schema = tool.get_openai_tool_schema()
            # For OpenAI: remove CAMEL's strict=true and additionalProperties:false
            # to avoid strict-mode schema validation errors with complex MCP schemas.
            if strict_openai:
                schema.get("function", {}).pop("strict", None)
                params = schema.get("function", {}).get("parameters", {})
                _strip_strict_mode(params)
            params = schema.get("function", {}).get("parameters", {})
            _fix_schema(params, strict_openai=strict_openai)
            if hasattr(tool, "openai_tool_schema"):
                tool.openai_tool_schema = schema
            elif hasattr(tool, "_openai_tool_schema"):
                tool._openai_tool_schema = schema
        except Exception:
            pass
        # Wrap function to truncate long outputs.
        # Preserve async_call so ChatAgent uses the native async MCP path.
        try:
            original_func = tool.func
            original_async_call = getattr(original_func, "async_call", None)

            def _truncating_wrapper(*args, _fn=original_func, _max=max_output_chars, **kwargs):
                result = _fn(*args, **kwargs)
                result_str = str(result)
                if len(result_str) > _max:
                    result_str = result_str[:_max] + f"\n...[truncated, total {len(result_str)} chars]"
                return result_str

            _truncating_wrapper.__name__ = getattr(original_func, "__name__", "tool")
            _truncating_wrapper.__doc__ = getattr(original_func, "__doc__", "")

            # Preserve async_call so ChatAgent can use the native async path
            if original_async_call is not None:
                async def _async_truncating_wrapper(*args, _afn=original_async_call, _max=max_output_chars, **kwargs):
                    result = await _afn(*args, **kwargs)
                    result_str = str(result)
                    if len(result_str) > _max:
                        result_str = result_str[:_max] + f"\n...[truncated, total {len(result_str)} chars]"
                    return result_str
                _truncating_wrapper.async_call = _async_truncating_wrapper  # type: ignore[attr-defined]

            tool.func = _truncating_wrapper
        except Exception:
            pass


class TaskAgent:
    def __init__(self, task_config: TaskConfig, model, max_steps: int = 100, debug: bool = False):
        self.task_config = task_config
        self.model = model
        self.max_steps = max_steps
        self.debug = debug
        self._done_flag = [False]

    async def _setup_workspace(self) -> str:
        workspace = os.path.abspath(self.task_config.agent_workspace)
        os.makedirs(workspace, exist_ok=True)
        init = self.task_config.initialization
        if init and init.workspace and os.path.exists(str(init.workspace)):
            await copy_folder_contents(str(init.workspace), workspace)
        for srv, d in [("arxiv_local", "arxiv_local_storage"),
                       ("memory", "memory"),
                       ("playwright_with_chunk", ".playwright_output")]:
            if srv in self.task_config.needed_mcp_servers:
                os.makedirs(os.path.join(workspace, d), exist_ok=True)
        return workspace

    def _run_preprocess(self):
        init = self.task_config.initialization
        if init and init.process_command:
            cmd = init.process_command
            # process_command may be a uv run -m ... command or a file path
            if True:
                print_color("[preprocess] running...", "yellow")
                r = subprocess.run(cmd.split(), capture_output=not self.debug, text=True)
                if r.returncode != 0:
                    print_color(f"[preprocess] failed: {(r.stderr or '')[:300]}", "red")
                else:
                    print_color("[preprocess] done.", "green")

    def _build_local_tools(self, workspace: str) -> List[FunctionTool]:
        needed = set(self.task_config.needed_local_tools or [])
        tools = []

        if "claim_done" in needed:
            self._done_flag = [False]
            tools.append(FunctionTool(make_claim_done(self._done_flag)))

        if "python_execute" in needed:
            tools.append(FunctionTool(make_python_execute(workspace)))

        if "handle_overlong_tool_outputs" in needed:
            save_fn, view_fn = make_overlong_tools(workspace)
            tools.append(FunctionTool(save_fn))
            tools.append(FunctionTool(view_fn))

        if "sleep" in needed:
            tools.append(FunctionTool(sleep))

        # Stub for manage_context / history (CAMEL handles memory internally)
        for name in ("manage_context", "history"):
            if name in needed:
                async def _stub(action: str = "") -> str:
                    f"""Stub for {name} — managed internally."""
                    return "OK"
                _stub.__name__ = name
                _stub.__doc__ = f"Stub for {name}."
                tools.append(FunctionTool(_stub))

        return tools

    def _save_log(self, status: TaskStatus, start_time: datetime, response=None, agent_history=None):
        log_path = self.task_config.log_file
        if not log_path:
            return
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)

        # Extract chat history and tool calls from response
        tool_calls = []
        chat_history = []
        if response is not None:
            raw_calls = response.info.get("tool_calls", [])
            for tc in raw_calls:
                try:
                    tool_calls.append(tc.as_dict() if hasattr(tc, "as_dict") else str(tc))
                except Exception:
                    tool_calls.append(str(tc))
            for msg in (response.msgs or []):
                try:
                    chat_history.append({"role": msg.role_name, "content": msg.content})
                except Exception:
                    pass

        # Full conversation from agent memory (all turns)
        full_history = []
        if agent_history:
            for msg in agent_history:
                try:
                    entry = {"role": msg.get("role", ""), "content": msg.get("content", "")}
                    if msg.get("tool_calls"):
                        entry["tool_calls"] = msg["tool_calls"]
                    if msg.get("tool_call_id"):
                        entry["tool_call_id"] = msg["tool_call_id"]
                    full_history.append(entry)
                except Exception:
                    full_history.append(str(msg))

        # traj_log.json: evaluator reads this (needs config + status)
        record = {
            "config": self.task_config.to_dict(),
            "status": status.value,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
        }
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        # traj.json: full conversation trajectory for analysis
        traj_path = str(Path(log_path).parent / "traj.json")
        traj = {
            "status": status.value,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "messages": full_history,
            "tool_calls": tool_calls,
        }
        with open(traj_path, "w", encoding="utf-8") as f:
            json.dump(traj, f, ensure_ascii=False, indent=2)

    async def run(self) -> TaskStatus:
        start_time = datetime.now()
        status = TaskStatus.FAILED
        toolkit = None
        response = None
        agent = None
        try:
            workspace = await self._setup_workspace()
            self._workspace = workspace
            self._run_preprocess()

            task_src_dir = os.path.abspath(os.path.join("tasks/finalpool", self.task_config.task_dir))
            mcp_clients = build_mcp_clients(self.task_config.needed_mcp_servers, workspace, task_dir=task_src_dir)
            toolkit = MCPToolkit(clients=mcp_clients)
            await toolkit.connect()

            mcp_tools = toolkit.get_tools()
            strict_openai = os.environ.get("MODEL_PLATFORM", "").lower() == "openai"
            _sanitize_tool_schemas(mcp_tools, strict_openai=strict_openai)
            local_tools = self._build_local_tools(workspace)
            all_tools = mcp_tools + local_tools
            # OpenAI API enforces a 128-tool limit; trim only for official OpenAI platform
            if (os.environ.get("MODEL_PLATFORM", "").lower() == "openai"
                    and len(all_tools) > 128):
                print_color(f"[agent] OpenAI tool limit: {len(all_tools)} tools, trimming to 128.", "yellow")
                all_tools = mcp_tools[:128 - len(local_tools)] + local_tools

            if self.debug:
                print_color(f"[agent] MCP tools ({len(mcp_tools)}): {[t.get_function_name() for t in mcp_tools]}", "cyan")
                print_color(f"[agent] Local tools: {[t.get_function_name() for t in local_tools]}", "cyan")

            default_sys_msg = (
                f"You are a helpful AI assistant. Your workspace directory is: {workspace}\n"
                "Complete the user's task using the provided tools. "
                "When you have finished all required work, call the claim_done tool to signal completion. "
                "Do not ask for confirmation — complete the task independently."
            )
            sys_msg = default_sys_msg
            if self.task_config.system_prompts and self.task_config.system_prompts.agent:
                sys_msg = self.task_config.system_prompts.agent

            agent = ChatAgent(
                system_message=sys_msg,
                model=self.model,
                tools=all_tools,
                max_iteration=self.max_steps,
                step_timeout=600,
                tool_execution_timeout=120,
            )

            task_str = self.task_config.task_str
            print_color(f"\n[task] {task_str[:300]}\n", "yellow")
            response = await agent.astep(BaseMessage.make_user_message("User", task_str))
            if self.debug:
                print_color(f"[agent] response.terminated={response.terminated}, done_flag={self._done_flag[0]}", "cyan")
                if response.msgs:
                    print_color(f"[agent] last msg: {response.msgs[-1].content[:300]}", "cyan")

            if self._done_flag[0]:
                status = TaskStatus.SUCCESS
                print_color("[agent] Done (claim_done called).", "green")
            elif response and response.terminated:
                status = TaskStatus.MAX_TURNS_REACHED
                print_color("[agent] Max iterations reached.", "yellow")
            else:
                status = TaskStatus.FAILED
                print_color("[agent] Ended without claim_done.", "red")

        except KeyboardInterrupt:
            status = TaskStatus.INTERRUPTED
        except Exception as e:
            print_color(f"[agent] Error: {e}", "red")
            if self.debug:
                traceback.print_exc()
        finally:
            if toolkit is not None:
                try:
                    await toolkit.disconnect()
                except Exception:
                    pass

        agent_history = None
        if agent is not None:
            try:
                agent_history = agent.chat_history
            except Exception:
                pass
        self._save_log(status, start_time, response=response, agent_history=agent_history)
        return status
