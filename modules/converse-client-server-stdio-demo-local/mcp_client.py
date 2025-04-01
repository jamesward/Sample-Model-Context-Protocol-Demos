from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, List
import asyncio
import json

class MCPClient:
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        self.session = None
        self._client = None
        self._resource_update_callbacks = []
        self._notification_task = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._notification_task:
            self._notification_task.cancel()
            try:
                await self._notification_task
            except asyncio.CancelledError:
                pass
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def _handle_incoming_messages(self):
        """Process incoming messages from the session"""
        async for message in self.session.incoming_messages:
            if isinstance(message, Exception):
                print(f"Error in message handling: {message}")
                continue
                
            if hasattr(message, 'method') and message.method == "resource/updated":
                uri = message.params.uri
                for callback in self._resource_update_callbacks:
                    try:
                        await callback(uri)
                    except Exception as e:
                        print(f"Error in resource update callback: {e}")

    async def connect(self):
        """Establishes connection to MCP server"""
        self._client = stdio_client(self.server_params)
        self.read, self.write = await self._client.__aenter__()
        session = ClientSession(self.read, self.write)
        self.session = await session.__aenter__()
        await self.session.initialize()
        
        # Start message handling task
        self._notification_task = asyncio.create_task(self._handle_incoming_messages())

    # Tools

    async def get_available_tools(self) -> List[Any]:
        """List available tools"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        response = await self.session.list_tools()
        print("Raw tools data:", response)  # Debug print
        
        # Extract the actual tools from the response
        tools = response.tools if hasattr(response, 'tools') else []
        
        # Convert tools to list of dictionaries with expected attributes
        formatted_tools = [
            {
                'name': tool.name,
                'description': str(tool.description) if tool.description is not None else "No description available",
                'inputSchema': {
                    'json': {
                        'type': 'object',
                        'properties': tool.inputSchema.get('properties', {}) if tool.inputSchema else {},
                        'required': tool.inputSchema.get('required', []) if tool.inputSchema else []
                    }
                }
            }
            for tool in tools
        ]
        print("Formatted tools:", json.dumps(formatted_tools, indent=2))  # Debug print
        return formatted_tools

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a tool with given arguments"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        result = await self.session.call_tool(tool_name, arguments=arguments)
        return result
    
    # Resources

    async def get_available_resources(self) -> List[Any]:
        """List available resources"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        resources = await self.session.list_resources()
        _, resources_list = resources
        _, resources_list = resources_list
        return resources_list
    
    async def get_resource(self, uri: str) -> Any:
        """Get a resource"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        resource = await self.session.read_resource(uri)
        return resource

    def on_resource_update(self, callback):
        """Register a callback to be called when resources are updated"""
        self._resource_update_callbacks.append(callback)