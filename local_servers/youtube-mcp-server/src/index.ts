import { startMcpServer } from './server.js';

// Start the MCP server (no API key needed - uses PostgreSQL backend)
startMcpServer()
    .then(() => {
        console.error('YouTube MCP Server (pg-backed) started successfully');
    })
    .catch(error => {
        console.error('Failed to start YouTube MCP Server:', error);
        process.exit(1);
    });
