import asyncio
from mcp import StdioServerParameters
from converse_agent import ConverseAgent
from converse_tools import ConverseToolManager
from mcp_client import MCPClient
import os
from datetime import datetime

# ANSI color codes for beautiful output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def clear_screen():
    """Clear the terminal screen using ANSI escape codes"""
    print('\033[2J\033[H', end='')

def print_welcome():
    """Print a welcome message"""
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}Welcome to AI Assistant!{Colors.END}")
    print(f"{Colors.CYAN}I'm here to help you with any questions or tasks.{Colors.END}")
    print(f"{Colors.CYAN}Type 'quit' to exit.{Colors.END}\n")

def print_tools(tools):
    """Print available tools in a nice format"""
    print(f"{Colors.CYAN}Available Tools:{Colors.END}")
    for tool in tools:
        print(f"  • {Colors.GREEN}{tool['name']}{Colors.END}: {tool['description']}")
    print()  # Add a blank line for spacing

def format_message(role: str, content: str) -> str:
    """Format a message with appropriate colors and styling"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if role == "user":
        return f"{Colors.BLUE}[{timestamp}] You: {Colors.END}{content}"
    else:
        return f"{Colors.GREEN}Assistant: {Colors.END}{content}"

async def handle_resource_update(uri: str):
    """Handle updates to resources from the MCP server"""
    print(f"{Colors.YELLOW}Resource updated: {uri}{Colors.END}")
    # You could trigger a refresh of the resource here if needed
    
async def main():
    """
    Main function that sets up and runs an interactive AI agent with tool integration.
    The agent can process user prompts and utilize registered tools to perform tasks.
    """
    # Initialize model configuration
    model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    # Set up the agent and tool manager
    agent = ConverseAgent(model_id)
    agent.tools = ConverseToolManager()

    # Define the agent's behavior through system prompt
    agent.system_prompt = """You are a helpful assistant that can use tools to help you answer 
questions and perform tasks."""

    # Create server parameters for stdio configuration
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=None
    )

    # Initialize MCP client with server parameters
    async with MCPClient(server_params) as mcp_client:
        # Register resource update handler
        mcp_client.on_resource_update(handle_resource_update)

        # # Fetch and display available resources
        # resources = await mcp_client.get_available_resources()
        # print("Available resources:", resources)

        # for resource in resources:
        #     try:
        #         await mcp_client.session.subscribe_resource(resource.uri)
        #     except Exception as e:
        #         print(f"Error subscribing to resource {resource.uri}: {e}")

        # Fetch available tools from the MCP client
        tools = await mcp_client.get_available_tools()

        # Register each available tool with the agent
        for tool in tools:
            agent.tools.register_tool(
                name=tool['name'],
                func=mcp_client.call_tool,
                description=tool['description'],
                input_schema={'json': tool['inputSchema']}
            )

        print_welcome()
        print_tools(tools)  # Print available tools after welcome message

        # Start interactive prompt loop
        while True:
            try:
                # Get user input and check for exit commands
                user_prompt = input(f"\n{Colors.BOLD}User: {Colors.END}")
                if user_prompt.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{Colors.CYAN}Goodbye! Thanks for chatting!{Colors.END}")
                    break
                
                # Skip empty input
                if not user_prompt.strip():
                    continue
                
                # Process the prompt and display the response
                print(f"\n{Colors.YELLOW}Thinking...{Colors.END}")
                response = await agent.invoke_with_prompt(user_prompt)
                print(f"\n{format_message('assistant', response)}")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.CYAN}Goodbye! Thanks for chatting!{Colors.END}")
                break
            except Exception as e:
                print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 