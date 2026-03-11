# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Build:**
```bash
npm run build
```
This compiles TypeScript and runs the CLI build script that generates the binary executable.

**Development:**
```bash
npm run dev
```
Runs the server in development mode with hot reloading using tsx watch.

**Testing:**
The project uses Vitest for testing. Run tests with:
```bash
npx vitest
```

**Execute locally:**
```bash
npx -y --prefix /path/to/local/notion-mcp-server @notionhq/notion-mcp-server
```

## Architecture Overview

This is a **Notion MCP (Model Context Protocol) Server** that bridges the Notion API with MCP-compatible clients like Claude Desktop. The architecture follows a layered approach:

### Core Components

**1. OpenAPI-to-MCP Conversion Layer** (`src/openapi-mcp-server/`)
- **Parser** (`openapi/parser.ts`): Converts OpenAPI 3.x specifications to MCP tool definitions
- **HTTP Client** (`client/http-client.ts`): Handles HTTP requests to the Notion API with proper authentication and error handling
- **MCP Proxy** (`mcp/proxy.ts`): Main orchestration layer that connects MCP tools to OpenAPI operations

**2. Server Initialization** (`src/init-server.ts`)
- Loads and validates the Notion OpenAPI specification from `scripts/notion-openapi.json`
- Creates the MCPProxy instance that handles tool calls

**3. Transport Layer** (`scripts/start-server.ts`)
- Supports **STDIO transport** (default) for standard MCP clients
- Supports **Streamable HTTP transport** for web-based clients
- Handles authentication via bearer tokens for HTTP transport
- Manages session state for HTTP connections

### Key Files

- **`scripts/notion-openapi.json`**: The OpenAPI specification for Notion API
- **`src/openapi-mcp-server/mcp/proxy.ts`**: Core MCP proxy that converts tool calls to API requests
- **`src/openapi-mcp-server/openapi/parser.ts`**: Converts OpenAPI schemas to JSON Schema for MCP tools
- **`scripts/start-server.ts`**: Main entry point with transport selection logic

### Authentication

The server supports two authentication methods:
1. **NOTION_TOKEN** environment variable (recommended)
2. **OPENAPI_MCP_HEADERS** environment variable with JSON headers

### Transport Modes

**STDIO (Default):**
- Standard MCP transport for clients like Claude Desktop
- Uses stdin/stdout for communication

**Streamable HTTP:**
- REST API endpoints at `/mcp` 
- Requires bearer token authentication
- Supports session management for persistent connections
- Health check endpoint at `/health`

## Development Notes

- The project is built as an ES module (`"type": "module"` in package.json)
- Uses TypeScript with strict mode enabled
- The build process creates both TypeScript declarations and a CLI binary
- File uploads are supported via multipart/form-data handling
- Error handling includes specific OpenAPI validation errors