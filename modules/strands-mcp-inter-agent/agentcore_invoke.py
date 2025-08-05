import os

import boto3
import json
import random
import string


region = os.environ.get("AWS_REGION", "us-east-1")

agent_arn = os.environ.get("AGENT_ARN")

agent_core_client = boto3.client("bedrock-agentcore", region_name=region)

response = agent_core_client.list_agent_runtimes()
print(response)

#
# payload = json.dumps({
#     "input": {"question": "list employees that have skills related to AI programming"}
# })
#
# session_id = "".join(random.choices(string.digits + string.ascii_lowercase, k=33))
#
# response = agent_core_client.invoke_agent_runtime(
#     agentRuntimeArn=agent_arn,
#     runtimeSessionId=session_id,  # Must be 33+ chars
#     payload=payload,
#     qualifier="DEFAULT"
# )
#
# response_body = response["response"].read()
# response_data = json.loads(response_body)
# print("Agent Response:", response_data)
