import os
import json
import boto3

region = os.environ.get("AWS_REGION", "us-east-1")

bedrock_agentcore_control = boto3.client("bedrock-agentcore-control", region_name=region)

agent_runtimes = bedrock_agentcore_control.list_agent_runtimes()
# print(agent_runtimes)

for agent_runtime in agent_runtimes["agentRuntimes"]:
    agent_runtime_detail = bedrock_agentcore_control.get_agent_runtime(
        agentRuntimeId=agent_runtime["agentRuntimeId"],
        agentRuntimeVersion=agent_runtime["agentRuntimeVersion"]
    )
    print(json.dumps(agent_runtime_detail, indent=2, default=str))
