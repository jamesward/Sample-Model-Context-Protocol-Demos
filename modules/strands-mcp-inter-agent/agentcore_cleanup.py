import os
import boto3

region = os.environ.get("AWS_REGION", "us-east-1")

def main():
    bedrock_agentcore_control = boto3.client("bedrock-agentcore-control", region_name=region)

    agent_runtimes = bedrock_agentcore_control.list_agent_runtimes()
    print(agent_runtimes)

    delete_response = bedrock_agentcore_control.delete_agent_runtime(agentRuntimeId="strands_mcp_inter_agent_hr_agent-4d9LFtBRxJ")
    print(delete_response)

if __name__ == "__main__":
    main()
