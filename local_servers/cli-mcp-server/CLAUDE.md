# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a secure Model Context Protocol (MCP) server implementation that provides controlled command-line execution capabilities. The server enables LLM applications to execute CLI commands with comprehensive security features including command whitelisting, path validation, and shell operator protection.

## Development Commands

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m unittest tests.test_cli_mcp_server

# Run tests with verbose output
python -m unittest -v tests.test_cli_mcp_server
```

### Building and Publishing
```bash
# Sync dependencies and update lockfile
uv sync

# Build package distributions
uv build

# Publish to PyPI (requires API token)
uv publish --token {YOUR_PYPI_API_TOKEN}
```

### Running the Server
```bash
# Run locally for development
uv run cli-mcp-server

# Run with MCP Inspector for debugging
npx @modelcontextprotocol/inspector uv --directory . run cli-mcp-server
```

## Architecture

### Core Components

- **`server.py`**: Main MCP server implementation containing:
  - `CommandExecutor`: Secure command execution engine with path validation and security controls
  - `SecurityConfig`: Configuration dataclass for security policies
  - Custom exception classes: `CommandSecurityError`, `CommandExecutionError`, `CommandTimeoutError`
  - Two MCP tools: `run_command` and `show_security_rules`

- **`__init__.py`**: Package entry point that exposes the `main()` function

### Security Architecture

The server implements multiple security layers:

1. **Command Whitelisting**: Only allowed commands can be executed (configurable via `ALLOWED_COMMANDS`)
2. **Flag Validation**: Command flags must be in the allowed list (configurable via `ALLOWED_FLAGS`)
3. **Path Normalization**: All file paths are validated to prevent directory traversal attacks
4. **Shell Operator Control**: Shell operators (&&, ||, |, >, etc.) are disabled by default but can be enabled
5. **Execution Limits**: Configurable timeouts and command length limits
6. **Working Directory Restriction**: Commands execute only within the specified allowed directory

### Environment Configuration

Required:
- `ALLOWED_DIR`: Base directory for command execution (must exist)

Optional (with defaults):
- `ALLOWED_COMMANDS`: Comma-separated commands or "all" (default: "ls,cat,pwd")
- `ALLOWED_FLAGS`: Comma-separated flags or "all" (default: "-l,-a,--help")
- `MAX_COMMAND_LENGTH`: Maximum command string length (default: 1024)
- `COMMAND_TIMEOUT`: Execution timeout in seconds (default: 30)
- `ALLOW_SHELL_OPERATORS`: Enable shell operators like &&, ||, | (default: false)

**Output Control:**
- `MAX_OUTPUT_LENGTH`: Maximum total output length (default: 10240)
- `MAX_STDOUT_LENGTH`: Maximum stdout length (default: 8192)
- `MAX_STDERR_LENGTH`: Maximum stderr length (default: 2048)
- `OUTPUT_TRUNCATE_MESSAGE`: Message shown when output is truncated (default: "...[output truncated]")

**Proxy Support:**
- `CLI_PROXY_ENABLED`: Enable proxy support (default: false)
- `CLI_PROXY_URL`: Proxy URL (also checks HTTP_PROXY if not set)

Example proxy configuration:
```bash
CLI_PROXY_ENABLED=true
CLI_PROXY_URL=http://proxy.company.com:8080
```

## Testing Strategy

The test suite in `tests/test_cli_mcp_server.py` covers:

- Basic command execution (pwd, ls)
- Security validation (shell operator blocking)
- Shell operator functionality when enabled
- Path handling and file operations
- Network operations (curl test when available)

Tests use a temporary directory and reload the server module to test different configurations.

## Package Management

- Uses `uv` for dependency management and building
- Python 3.10+ required
- Single dependency: `mcp>=1.10.1`
- Entry point defined in `pyproject.toml` as `cli-mcp-server = "cli_mcp_server:main"`