from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
import logging
import sys

# Configure logging to write to both file and stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Create a FastMCP instance
mcp = FastMCP("Demo Server")

@mcp.tool()
def calculator(operation: str, x: float, y: float) -> Dict[str, Any]:
    """A simple calculator that can add, subtract, multiply, and divide"""
    logger.info(f"Calculator called with operation={operation}, x={x}, y={y}")
    
    result = None
    if operation == "add":
        result = x + y
    elif operation == "subtract":
        result = x - y
    elif operation == "multiply":
        result = x * y
    elif operation == "divide":
        if y == 0:
            logger.error("Division by zero attempted")
            raise ValueError("Cannot divide by zero")
        result = x / y
    
    logger.info(f"Calculator result: {result}")
    return {"result": result}

@mcp.tool()
def weather(location: str) -> Dict[str, Any]:
    """Get the current weather for a location"""
    logger.info(f"Weather tool called for location: {location}")
    
    # This is a mock implementation
    response = {
        "temperature": 72,
        "condition": "sunny",
        "location": location
    }
    logger.info(f"Weather response: {response}")
    return response

if __name__ == "__main__":
    logger.info("Starting MCP Demo Server...")
    try:
        # Start the server
        mcp.run()
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise 