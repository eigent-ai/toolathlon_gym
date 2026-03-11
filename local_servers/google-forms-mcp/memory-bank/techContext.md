# Technical Context

## Core Technologies

*   **Programming Languages:** TypeScript (compiles to JavaScript)
*   **Frameworks/Libraries:**
    *   `@modelcontextprotocol/sdk`: For MCP server implementation.
    *   `googleapis`: Google API client library for Node.js (specifically for Forms API).
    *   `google-auth-library`: For Google API authentication (OAuth2).
    *   `axios`: HTTP client (likely used by googleapis or for other requests).
    *   `open`: To open URLs in the browser (used by `get-refresh-token.ts`).
    *   `server-destroy`: To gracefully shut down the HTTP server in `get-refresh-token.ts`.
*   **Databases:** None (stateless server, relies on Google Forms for data storage).
*   **Runtime Environments:** Node.js

## Development Environment Setup

*   **Required Software:** Node.js (version not specified, but compatible with ES modules and modern TypeScript).
*   **Key Configuration Files:**
    *   `package.json`: Defines project metadata, scripts, and dependencies.
    *   `tsconfig.json`: TypeScript compiler options.
    *   Environment Variables: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` are crucial for operation.
*   **Build Process:**
    *   `npm run build`: Compiles TypeScript in `src/` to JavaScript in `build/` and makes `build/index.js` executable. This script is `tsc && node -e "require('fs').chmodSync('build/index.js', '755')"`.
    *   `npm run build:token`: Compiles TypeScript using `tsconfig.json` (likely for `get-refresh-token.ts`). This script is `tsc -p tsconfig.json`.
*   **Running the Project Locally:**
    *   `npm run start` or `node build/index.js`: Runs the main MCP server.
    *   `npm run get-refresh-token`: Builds and runs the script to obtain a Google API refresh token. This script is `npm run build:token && node build/get-refresh-token.js`.
*   **Testing:** No dedicated test scripts or frameworks are specified in `package.json`.

## Dependencies

*   **Key External Services:**
    *   Google Forms API: For all form-related operations.
    *   Google Drive API: Scope `https://www.googleapis.com/auth/drive` is requested by `get-refresh-token.ts`, though its direct use isn't apparent in `index.ts`. It might be implicitly required by Forms API for certain operations or a remnant.
    *   Authentication methods: OAuth 2.0 with Client ID, Client Secret, and a Refresh Token.
*   **Critical Libraries/Packages:**
    *   `@modelcontextprotocol/sdk`: Core for MCP functionality.
    *   `googleapis`: Essential for interacting with Google services.
*   **Version Management:** `package-lock.json` manages precise dependency versions.

## Technical Constraints

*   Requires valid Google Cloud OAuth 2.0 credentials and a refresh token.
*   Internet connectivity is required to reach Google APIs.
*   The server operates via stdio when connected to an MCP client.

## Code Style & Conventions

*   TypeScript is used, implying static typing.
*   ES module syntax (`import`/`export`) is used.
*   No specific linter (like ESLint) or formatter (like Prettier) is listed in `devDependencies`, but standard TypeScript best practices are generally followed.

## Deployment (If applicable)

*   The server is intended to be run locally as an MCP server, typically configured within an MCP client application (e.g., Claude desktop app).
*   The `README.md` provides instructions for configuring it with the Claude desktop app, including setting environment variables and the path to the built `index.js` file.
