import os
import sys

import boto3
import string
import secrets
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

region = os.environ.get("AWS_REGION", "us-east-1")

pool_id = os.environ.get("COGNITO_POOL_ID")
client_id = os.environ.get("COGNITO_CLIENT_ID")
agent_arn = os.environ.get("AGENT_ARN")

if not pool_id or not client_id or not agent_arn:
    print("Error: COGNITO_POOL_ID or COGNITO_CLIENT_ID or AGENT_ARN environment variable is not set")
    sys.exit(1)

cognito_client = boto3.client('cognito-idp', region_name=region)

username = ''.join(secrets.choice(string.ascii_letters) for _ in range(8))
temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
permanent_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

cognito_client.admin_create_user(
    UserPoolId=pool_id,
    Username=username,
    TemporaryPassword=temp_password,
    MessageAction='SUPPRESS'
)

print(f"User {username} created successfully")

cognito_client.admin_set_user_password(
    UserPoolId=pool_id,
    Username=username,
    Password=permanent_password,
    Permanent=True
)

response = cognito_client.initiate_auth(
    ClientId=client_id,
    AuthFlow='USER_PASSWORD_AUTH',
    AuthParameters={
        'USERNAME': username,
        'PASSWORD': permanent_password
    }
)

bearer_token = response['AuthenticationResult']['AccessToken']
# print(f"Bearer token: {bearer_token}")

encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
headers = {"authorization": f"Bearer {bearer_token}","Content-Type":"application/json"}
print(f"Invoking: {mcp_url}")

async def main():
    async with streamablehttp_client(mcp_url, headers, timeout=120, terminate_on_close=False) as (
            read_stream,
            write_stream,
            _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_result = await session.list_tools()
            print(tool_result)

asyncio.run(main())


# agent_core_client = boto3.client("bedrock-agentcore", region_name=region)

# response = agent_core_client.list_agent_runtimes()
# print(response)

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
