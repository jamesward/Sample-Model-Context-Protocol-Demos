import os
import boto3

region = os.environ.get("AWS_REGION", "us-east-1")

bedrock_agentcore_control = boto3.client("bedrock-agentcore-control", region_name=region)

agent_runtimes = bedrock_agentcore_control.list_agent_runtimes()
print(agent_runtimes)
