import { FastMCP, FastMCPSession } from "fastmcp";
import { env, APP_VERSION } from './config/environment';
import { registerTools } from './tools';
import { startHealthServer } from './services/health';

// Print startup banner
console.log(`
=== ${env.PROJECT_NAME} ===
Version: ${APP_VERSION}
Mode: ${env.NODE_ENV}
===================
`);

// Create MCP server instance
const server = new FastMCP({
    name: env.PROJECT_NAME,
    version: APP_VERSION
});

// Handle client connections
server.on("connect", (event: { session: FastMCPSession }) => {
    console.log("Client connected");
    
    // Log session errors without crashing
    event.session.on('error', (event: { error: Error }) => {
        console.warn('Session error:', event.error);
    });
});

server.on("disconnect", () => {
    console.log("Client disconnected");
});

// Register tools and start servers
async function startServer() {
    try {
        // Register MCP tools
        registerTools(server);

        // Start health check endpoint
        startHealthServer();

        // Start MCP server
        await server.start({
            transportType: "sse",
            sse: {
                endpoint: "/sse",
                port: 8000
            }
        });

        console.log(`
Server is running!
- MCP endpoint: http://localhost:8000/sse
- Health check: http://localhost:8001/health
        `);
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Start the server
startServer();

// Handle uncaught errors
process.on('uncaughtException', (error: Error) => {
    console.error('Uncaught exception:', error);
    // Don't exit the process, just log the error
});

process.on('unhandledRejection', (error: Error) => {
    console.error('Unhandled rejection:', error);
    // Don't exit the process, just log the error
}); 