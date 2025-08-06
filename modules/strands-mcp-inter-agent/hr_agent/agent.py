import os
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp.mcp_client import MCPClient
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

EMPLOYEE_AGENT_URL = os.environ.get("EMPLOYEE_AGENT_URL", "http://localhost:8001/mcp/")
print(EMPLOYEE_AGENT_URL)
hr_mcp_client = MCPClient(lambda: streamablehttp_client(EMPLOYEE_AGENT_URL))


bedrock_model = BedrockModel(
    model_id="amazon.nova-micro-v1:0",
    region_name="us-east-1",
)

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """HR Agent"""
    with hr_mcp_client:
        tools = hr_mcp_client.list_tools_sync()
        agent = Agent(model=bedrock_model, tools=tools) #, callback_handler=None)
        user_message = payload.get("question")
        result = agent(user_message)
        return {"result": result.message}

if __name__ == "__main__":
    port=int(os.environ.get("PORT", "8000"))
    app.run(port=port)
