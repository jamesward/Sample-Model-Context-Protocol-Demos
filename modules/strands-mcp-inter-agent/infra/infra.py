import aws_cdk as cdk

from aws_cdk import (
    Stack,
    aws_iam as iam,
)

# from aws_cdk.aws_lambda_python_alpha import (
#     PythonFunction,
#     PythonLayerVersion,
# )
# from aws_cdk.aws_lambda import Runtime
from uv_python_lambda import PythonFunction
from constructs import Construct

agent_name = "strands-mcp-inter-agent"

class BedrockAgentCoreRuntimeRole(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        account_id = Stack.of(self).account
        region = Stack.of(self).region

        permissions_policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    sid="ECRImageAccess",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ecr:BatchGetImage",
                        "ecr:GetDownloadUrlForLayer"
                    ],
                    resources=[
                        f"arn:aws:ecr:{region}:{account_id}:repository/*"
                    ]
                ),

                iam.PolicyStatement(
                    sid="ECRTokenAccess",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ecr:GetAuthorizationToken"
                    ],
                    resources=["*"]
                ),

                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "logs:DescribeLogStreams",
                        "logs:CreateLogGroup"
                    ],
                    resources=[
                        f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
                    ]
                ),

                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "logs:DescribeLogGroups"
                    ],
                    resources=[
                        f"arn:aws:logs:{region}:{account_id}:log-group:*"
                    ]
                ),

                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    resources=[
                        f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
                    ]
                ),

                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "xray:PutTraceSegments",
                        "xray:PutTelemetryRecords",
                        "xray:GetSamplingRules",
                        "xray:GetSamplingTargets"
                    ],
                    resources=["*"]
                ),

                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["cloudwatch:PutMetricData"],
                    resources=["*"],
                    conditions={
                        "StringEquals": {
                            "cloudwatch:namespace": "bedrock-agentcore"
                        }
                    }
                ),

                iam.PolicyStatement(
                    sid="GetAgentAccessToken",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "bedrock-agentcore:GetWorkloadAccessToken",
                        "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                        "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
                    ],
                    resources=[
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/{agent_name}-*"
                    ]
                ),

                iam.PolicyStatement(
                    sid="BedrockModelInvocation",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    resources=[
                        "arn:aws:bedrock:*::foundation-model/*",
                        f"arn:aws:bedrock:{region}:{account_id}:*"
                    ]
                )
            ]
        )

        self.role = iam.Role(
            self,
            "BedrockAgentCoreRuntimeRole",
            role_name="BedrockAgentCoreRuntimeRole",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            inline_policies={
                "permissions": permissions_policy
            },
            description="Execution role for Amazon Bedrock AgentCore Runtime"
        )


class BedrockAgentCoreStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # custom_resource_agentcore_runtime_lambda_layer = PythonLayerVersion(self, 'DependenciesLayer', entry="./customresources")

        # custom_resource_agentcore_runtime_lambda = PythonFunction(
        #     self,
        #     "CustomResourceAgentCoreRuntimeLambda",
        #     entry="./customresources/agentcoreruntime.py",
        #     runtime=Runtime.PYTHON_3_13,
        #     layers=[
        #         PythonLayerVersion(self, 'DependenciesLayer', entry="./customresources")
        #     ]
        # )



        custom_resource_agentcore_runtime_lambda = PythonFunction(
            self,
            "CustomResourceAgentCoreRuntimeLambda",
            root_dir="./infra/customresources",
            index="agentcoreruntime.py",
        )

        agentcore_role = BedrockAgentCoreRuntimeRole(self,"AgentCoreRole")

        cdk.CfnOutput(self, "agent_role", value=agentcore_role.role.role_arn)

app = cdk.App()

BedrockAgentCoreStack(app, "BedrockAgentCoreStack")

app.synth()
