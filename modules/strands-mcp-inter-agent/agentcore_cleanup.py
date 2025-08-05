import os
from typing import Optional

import boto3

region = os.environ.get("AWS_REGION", "us-east-1")

agent_arn = os.environ.get("AGENT_ARN")

bedrock_agentcore_control = boto3.client("bedrock-agentcore-control", region_name=region)

def find_agent_runtime_id(target_arn) -> Optional[str]:
    agent_runtimes = bedrock_agentcore_control.list_agent_runtimes()
    print(agent_runtimes)

    agent_runtimes = agent_runtimes.get('agentRuntimes', [])

    matching_runtime = next(
        (runtime for runtime in agent_runtimes
         if runtime['agentRuntimeArn'] == target_arn),
        None
    )

    return matching_runtime['agentRuntimeId']


def main():
    maybe_agent_runtime_id = find_agent_runtime_id(agent_arn)

    if maybe_agent_runtime_id is None:
        print(f"No agent runtime found for ARN: {agent_arn}")
        return
    else:
        print(maybe_agent_runtime_id)
        delete_response = bedrock_agentcore_control.delete_agent_runtime(agentRuntimeId=maybe_agent_runtime_id)
        print(delete_response)

if __name__ == "__main__":
    main()
