import { ConverseAgent } from './converse/ConverseAgent.js';
import { ConverseTools } from './converse/ConverseTools.js';
import { MCPClient } from './MCPClient.js';
import { bedrockConfig, serverConfig } from './config/bedrock.js';
import chalk from 'chalk';

const SYSTEM_PROMPT = `You are a helpful assistant that can use tools to help you answer questions and perform tasks.

When using tools, follow these guidelines to be efficient:
1. Plan your tool usage before making calls - determine exactly what information you need
2. Make each tool call count - don't repeat the same call with the same parameters
3. Only make additional tool calls if the information you have is insufficient
4. Trust the results you get - don't make verification calls unless explicitly asked
5. When getting location-based information (weather, time, etc.), get the location info once and reuse it

Remember: Each tool call is expensive, so use them judiciously while still providing accurate and helpful responses.`;

export class MCPConverseClient extends MCPClient {
    private converseAgent: ConverseAgent;
    private converseTools: ConverseTools;

    constructor(serverUrl: string = serverConfig.url, modelId: string = bedrockConfig.modelId) {
        super(serverUrl);
        this.converseAgent = new ConverseAgent(modelId, bedrockConfig.region, SYSTEM_PROMPT);
        this.converseTools = new ConverseTools();
    }

    async connect(): Promise<void> {
        await super.connect();
        await this.setupTools();
    }

    private async setupTools(): Promise<void> {
        try {
            // Fetch available tools from the server
            const tools = await this.getAvailableTools();
            console.log(chalk.cyan('Available Tools:'));
            
            // Register each tool
            for (const tool of tools) {
                const schema = {
                    type: tool.inputSchema.type || 'object',
                    properties: tool.inputSchema.properties || {},
                    required: Array.isArray(tool.inputSchema.required) ? tool.inputSchema.required : []
                };
                
                this.converseTools.registerTool(
                    tool.name,
                    async (name: string, input: any) => {
                        return await this.callTool(name, input);
                    },
                    tool.description,
                    schema
                );
                console.log(chalk.green(`  • ${tool.name}: `) + tool.description);
            }
            console.log(); // Add blank line for spacing

            // Set the tools in the converse agent
            this.converseAgent.setTools(this.converseTools);
        } catch (error) {
            console.error(chalk.red('Error setting up tools:'), error);
            throw error;
        }
    }

    async processUserInput(input: string): Promise<void> {
        try {
            if (!input.trim()) {
                return;
            }
            
            const timestamp = new Date().toLocaleTimeString();
            console.log(chalk.blue(`[${timestamp}] You: `) + input);
            console.log(chalk.yellow('Thinking...'));
            
            const response = await this.converseAgent.invokeWithPrompt(input);
            console.log(chalk.green('Assistant: ') + response);
        } catch (error) {
            console.error(chalk.red('Error: ') + error);
        }
    }
} 