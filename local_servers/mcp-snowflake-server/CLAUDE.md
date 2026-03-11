# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Server
- **Local development**: `uv run mcp_snowflake_server` (requires .env with connection details)
- **With TOML config**: `uv run mcp_snowflake_server --connections-file path/to/connections.toml --connection-name development`
- **With write permissions**: Add `--allow-write` flag to enable INSERT/UPDATE/DELETE/CREATE operations

### Testing and Quality
- **Type checking**: `uv run pyright` (configured in pyproject.toml dev-dependencies)
- **Dependency management**: Uses `uv` package manager with `uv.lock` file

### Configuration
- **Environment variables**: Use `SNOWFLAKE_*` prefix (e.g., `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`)
- **TOML config**: See `example_connections.toml` for multiple environment setup
- **Runtime filtering**: `runtime_config.json` excludes temp tables/schemas by default

## Architecture Overview

This is a Model Context Protocol (MCP) server that provides Snowflake database interaction through tools and resources.

### Core Components

**Main Entry Point** (`__init__.py`):
- Handles argument parsing and configuration loading
- Supports both environment variables and TOML-based configuration
- Manages authentication methods (password, private key, external browser)

**Server Implementation** (`server.py`):
- MCP server using `mcp.server.stdio` 
- Defines tools for database operations and resources for data insights
- Uses decorator pattern for error handling (`handle_tool_errors`)

**Database Client** (`db_client.py`):
- `SnowflakeDB` class manages Snowpark sessions
- Handles connection lifecycle and authentication refresh (1800s expiry)
- Supports private key authentication with cryptography library

**SQL Analysis** (`write_detector.py`):
- `SQLWriteDetector` parses SQL using `sqlparse` 
- Detects write operations (INSERT, UPDATE, DELETE, CREATE, etc.)
- Analyzes CTEs (WITH clauses) for nested write operations

**Data Serialization** (`serialization.py`):
- Converts query results to YAML/JSON formats
- Handles pandas DataFrame serialization

### Key Features

**Tools Exposed**:
- `read_query`: Execute SELECT statements
- `write_query`: Execute write operations (when `--allow-write` enabled)
- `create_table`: Create new tables (when `--allow-write` enabled)
- `list_databases/schemas/tables`: Schema exploration
- `describe_table`: Table column information
- `append_insight`: Add insights to memo resource

**Resources**:
- `memo://insights`: Aggregates data insights discovered during analysis
- `context://table/{table_name}`: Per-table schema summaries (when prefetch enabled)

**Security**:
- Write operations disabled by default
- SQL parsing validates query types before execution
- Private key authentication supported
- Configurable exclusion patterns for sensitive data

### Configuration Patterns

The server supports flexible configuration through:
1. Environment variables with `SNOWFLAKE_` prefix
2. TOML files for multiple environments (production, staging, development)
3. Command-line arguments (highest precedence)

Connection precedence: TOML config > CLI args > environment variables

### Dependencies

Built on:
- `mcp>=1.0.0`: Model Context Protocol implementation
- `snowflake-connector-python`: Database connectivity
- `snowflake-snowpark-python`: Modern DataFrame API
- `sqlparse`: SQL parsing and analysis
- `pandas`: Data manipulation
- `tomli/tomllib`: TOML configuration parsing