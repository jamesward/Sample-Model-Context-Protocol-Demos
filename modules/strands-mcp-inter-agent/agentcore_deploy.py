import os
import json
import boto3
from botocore.exceptions import ClientError

region = os.environ.get("AWS_REGION", "us-east-1")

def create_bedrock_agent_role():
    """Create IAM role for Bedrock Agent Core if it doesn't exist"""

    sts_client = boto3.client('sts')

    response = sts_client.get_caller_identity()
    account_id = response['Account']

    iam_client = boto3.client("iam", region_name=region)
    role_name = "StrandsMCPInterAgentBedrockAgentCoreRole"

    # Trust policy for Bedrock Agent Core
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AssumeRolePolicy",
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": account_id
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"
                    }
                }
            }
        ]
    }

    # Permissions policy for Bedrock Agent Core
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ECRImageAccess",
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer"
                ],
                "Resource": [
                    f"arn:aws:ecr:{region}:{account_id}:repository/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:DescribeLogStreams",
                    "logs:CreateLogGroup"
                ],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:DescribeLogGroups"
                ],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
                ]
            },
            {
                "Sid": "ECRTokenAccess",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                    "xray:GetSamplingRules",
                    "xray:GetSamplingTargets"
                ],
                "Resource": [ "*" ]
            },
            {
                "Effect": "Allow",
                "Resource": "*",
                "Action": "cloudwatch:PutMetricData",
                "Condition": {
                    "StringEquals": {
                        "cloudwatch:namespace": "bedrock-agentcore"
                    }
                }
            },
            {
                "Sid": "GetAgentAccessToken",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
                ],
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/strands_mcp_inter_agent_*"
                ]
            },
            {
                "Sid": "BedrockModelInvocation",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*",
                    f"arn:aws:bedrock:{region}:{account_id}:*"
                ]
            }
        ]
    }

    try:
        # Check if role already exists
        try:
            role_response = iam_client.get_role(RoleName=role_name)
            print(f"Role {role_name} already exists")
            return role_response["Role"]["Arn"]
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchEntity":
                raise

        # Create the role
        print(f"Creating IAM role: {role_name}")
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Bedrock Agent Core runtime"
        )

        # Create and attach the permissions policy
        policy_name = "BedrockAgentCorePolicy"
        policy_response = iam_client.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(permissions_policy),
            Description="Permissions policy for Bedrock Agent Core"
        )

        # Attach the policy to the role
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_response["Policy"]["Arn"]
        )

        # todo: attaching the policy takes a minute so don't continue until it is complete

        print(f"Successfully created role: {role_response["Role"]["Arn"]}")
        return role_response["Role"]["Arn"]

    except ClientError as e:
        print(f"Error creating IAM role: {e}")
        raise

def main():
    bedrock_client = boto3.client("bedrock-agentcore-control", region_name=region)

    image = os.environ.get("ECR_REPO") + "/strands-mcp-inter-agent:latest"

    # Get or create the IAM role
    agent_role_arn = os.environ.get("AGENT_ROLE_ARN")
    if not agent_role_arn:
        print("AGENT_ROLE_ARN not provided, creating IAM role...")
        agent_role_arn = create_bedrock_agent_role()
        print(f"Using role ARN: {agent_role_arn}")
    else:
        print(f"Using provided role ARN: {agent_role_arn}")

    try:
        hr_agent_create_response = bedrock_client.create_agent_runtime(
            agentRuntimeName="strands_mcp_inter_agent_hr_agent",
            agentRuntimeArtifact={
                "containerConfiguration": {
                    "containerUri": image
                }
            },
            networkConfiguration={"networkMode":"PUBLIC"},
            roleArn=agent_role_arn
        )

        print("Agent runtime created successfully:")
        print(hr_agent_create_response)

    except ClientError as e:
        print(f"Error creating agent runtime: {e}")
        raise

if __name__ == "__main__":
    main()
