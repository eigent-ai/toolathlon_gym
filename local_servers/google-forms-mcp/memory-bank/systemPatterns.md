# System Patterns

## System Architecture Overview

*   This project is an MCP (Model Context Protocol) server designed to run as a local process and communicate with an MCP client (e.g., Claude desktop app) via stdio.
*   It acts as a bridge between the MCP client and the Google Forms API.
*   The server is stateless, meaning it doesn't store any form data or user session information itself; all state is managed by Google Forms.
*   Authentication with Google Forms API is handled using OAuth 2.0, with credentials (Client ID, Client Secret, Refresh Token) provided via environment variables.

    ```mermaid
    graph TD
        MCPClient["MCP Client (e.g., Claude App)"] -- Stdio --> GCFormsServer["GoogleFormsServer (Node.js/TypeScript)"]
        GCFormsServer -- OAuth 2.0 --> GoogleAuth["Google OAuth 2.0 Service"]
        GCFormsServer -- API Calls --> GoogleFormsAPI["Google Forms API"]
        GoogleFormsAPI -- Stores/Retrieves Data --> GoogleStorage["Google Cloud Storage (for Forms)"]
        
        subgraph "Local Machine"
            MCPClient
            GCFormsServer
        end

        subgraph "Google Cloud Platform"
            GoogleAuth
            GoogleFormsAPI
            GoogleStorage
        end
    ```

## Key Technical Decisions & Rationale

*   **MCP Server Model:** Chosen to integrate with MCP clients, providing a standardized way to expose Google Forms functionality.
    *   *Rationale:* Enables AI assistants or other tools to programmatically interact with Google Forms.
*   **Node.js and TypeScript:** Standard choice for MCP server development, offering good asynchronous capabilities and type safety.
    *   *Rationale:* Leverages the JavaScript ecosystem and provides robust development features.
*   **OAuth 2.0 with Refresh Token:** Standard and secure method for Google API authentication for server-side applications.
    *   *Rationale:* Allows long-term access without repeatedly asking the user to authenticate, suitable for a server process.
*   **Separate Refresh Token Acquisition Script (`get-refresh-token.ts`):** Isolates the one-time user interaction needed for OAuth consent from the main server logic.
    *   *Rationale:* Simplifies server startup and keeps the main server non-interactive. The script uses a local HTTP server and opens a browser for the consent flow.
*   **Stdio Transport for MCP:** Common for local MCP servers.
    *   *Rationale:* Simple and direct communication channel between the client and the local server process.

## Design Patterns in Use

*   **Server/Service Facade:** The `GoogleFormsServer` class acts as a facade, simplifying interactions with the more complex Google Forms API and MCP SDK.
*   **Request/Response Handling:** The MCP server uses a request/response pattern for tool calls, typical of such protocols.
*   **Environment Variable Configuration:** Configuration (API keys) is managed via environment variables, a common pattern for server applications.
*   **Error Handling:** Tool execution methods use try-catch blocks to handle errors from the Google Forms API and return structured error responses to the MCP client. `McpError` is used for standardized error reporting.

## Component Relationships & Interactions

*   **`GoogleFormsServer` (in `src/index.ts`):**
    *   Initializes the MCP `Server` instance from `@modelcontextprotocol/sdk`.
    *   Sets up an `OAuth2Client` from `google-auth-library` using environment variables.
    *   Initializes the `google.forms` API client.
    *   Defines tool handlers for `ListToolsRequestSchema` and `CallToolRequestSchema`.
    *   Maps tool names (e.g., `create_form`) to specific methods within the class.
    *   Connects to an MCP client via `StdioServerTransport`.
*   **`get-refresh-token.ts`:**
    *   A standalone script.
    *   Uses `google.auth.OAuth2` to generate an authorization URL.
    *   Starts a temporary local HTTP server to receive the OAuth callback.
    *   Uses the `open` library to direct the user to the Google consent screen.
    *   Exchanges the authorization code for tokens (including the refresh token).
    *   Prints the refresh token to the console for the user.
*   **MCP SDK (`@modelcontextprotocol/sdk`):** Provides the `Server` class, transport mechanisms, and schema definitions for MCP communication.
*   **Google APIs (`googleapis`, `google-auth-library`):** Provide the necessary clients and authentication mechanisms to interact with Google services.

## Data Flow

*   **Tool Call (e.g., `create_form`):**
    1.  MCP Client sends a `CallToolRequest` (JSON over stdio) to `GoogleFormsServer`.
    2.  `GoogleFormsServer` routes the request to the `createForm` method.
    3.  `createForm` constructs a request for the Google Forms API.
    4.  The `OAuth2Client` (using the refresh token) transparently handles access token acquisition/refresh if needed.
    5.  The `google.forms.forms.create()` method sends an HTTPS request to the Google Forms API.
    6.  Google Forms API processes the request and returns a response (e.g., new form ID).
    7.  `createForm` formats the API response into an MCP tool result.
    8.  `GoogleFormsServer` sends the result back to the MCP Client (JSON over stdio).
*   **Refresh Token Acquisition:**
    1.  User runs `node build/get-refresh-token.js`.
    2.  Script starts a local HTTP server on `http://localhost:3000`.
    3.  Script generates a Google OAuth consent URL and opens it in the user's browser.
    4.  User authenticates with Google and grants permissions.
    5.  Google redirects the browser to `http://localhost:3000/oauth2callback` with an authorization code.
    6.  The local HTTP server receives the code.
    7.  Script exchanges the code for a refresh token via a request to Google's token endpoint.
    8.  Script prints the refresh token to the console.

## Error Handling & Resilience

*   The main server (`src/index.ts`) includes a global `server.onerror` handler to log MCP errors.
*   Individual tool execution methods (e.g., `createForm`, `addTextQuestion`) use `try-catch` blocks.
*   Errors from the Google Forms API or invalid parameters result in an `McpError` being thrown or a structured error object being returned to the client, including an `ErrorCode` and a message.
*   The `get-refresh-token.ts` script also includes `try-catch` blocks and attempts to return HTML error pages if issues occur during the OAuth flow.
*   The server checks for required environment variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`) at startup and throws an error if they are missing.

## Scalability & Performance Considerations

*   As a local server instance, scalability is primarily limited by the user's machine and Google Forms API rate limits.
*   The server is designed for single-user interaction via an MCP client, not high-throughput concurrent use.
*   Performance depends on the responsiveness of the Google Forms API.
*   All API calls are asynchronous (`async/await`) to prevent blocking the Node.js event loop.
