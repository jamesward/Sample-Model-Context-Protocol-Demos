import os
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.fastmcp import FastMCP
from strands import Agent
from strands.tools.mcp.mcp_client import MCPClient
from strands.models import BedrockModel

port = int(os.environ.get('PORT', 8001))

EMPLOYEE_INFO_ARN=os.environ.get("EMPLOYEE_INFO_ARN", None)
REGION=os.environ.get("AWS_REGION", "us-east-1")
if EMPLOYEE_INFO_ARN is None:
    EMPLOYEE_INFO_URL = "http://localhost:8002/mcp/"
else:
    EMPLOYEE_INFO_URL =  f"https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{EMPLOYEE_INFO_ARN.replace(':', '%3A').replace('/', '%2F')}/invocations?qualifier=DEFAULT"

print(EMPLOYEE_INFO_URL)

employee_mcp_client = MCPClient(lambda: streamablehttp_client(EMPLOYEE_INFO_URL))

bedrock_model = BedrockModel(
    model_id="amazon.nova-micro-v1:0",
    region_name="us-east-1",
)

def employee_agent(question: str):
    with employee_mcp_client:
        tools = employee_mcp_client.list_tools_sync()

        agent = Agent(model=bedrock_model, tools=tools, system_prompt="you must abbreviate employee first names and list all their skills", callback_handler=None)

        return agent(question)

mcp = FastMCP("employee-agent", stateless_http=True, host="0.0.0.0", port=port)

@mcp.tool()
def inquire(question: str) -> list[str]:
    """answers questions related to our employees"""

    return [
        content["text"]
        for content in employee_agent(question).message["content"]
        if "text" in content
    ]

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
