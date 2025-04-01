import { MCPConverseClient } from './MCPConverseClient.js';
import * as readline from 'readline';
import chalk from 'chalk';

const DEFAULT_SERVER_URL = 'http://mcp-server:8000/sse';

async function main() {
    const serverUrl = process.env.MCP_SSE_URL || DEFAULT_SERVER_URL;
    const client = new MCPConverseClient(serverUrl);

    try {
        await client.connect();
        console.log(chalk.cyan('Connected to MCP server'));
        console.log(chalk.cyan('Type "quit" or "exit" to end the session\n'));

        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        rl.setPrompt(chalk.blue('> '));
        rl.prompt();

        rl.on('line', async (line) => {
            const input = line.trim();
            
            if (input.toLowerCase() === 'exit' || input.toLowerCase() === 'quit') {
                await client.close();
                rl.close();
                return;
            }

            if (!input) {
                rl.prompt();
                return;
            }

            await client.processUserInput(input);
            rl.prompt();
        });

        rl.on('close', () => {
            console.log(chalk.cyan('\nGoodbye!'));
            process.exit(0);
        });
    } catch (error) {
        console.error(chalk.red('Error:'), error);
        process.exit(1);
    }
}

main(); 