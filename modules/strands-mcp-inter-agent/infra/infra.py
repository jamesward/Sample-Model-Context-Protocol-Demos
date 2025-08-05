import aws_cdk

from constructs import Construct

from buildpack_image_asset import BuildpackImageAsset
from bedrock_agentcore_runtime import BedrockAgentCoreRuntime

# agent_name = "strands-mcp-inter-agent"

class BedrockAgentCoreStack(aws_cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        employee_server_image = BuildpackImageAsset(self, "EmployeeServerImage",
                                                    source_path="./",
                                                    builder="public.ecr.aws/heroku/builder:24",
                                                    run_image="public.ecr.aws/heroku/heroku:24",
                                                    platform="linux/amd64",
                                                    default_process="employee-server",
                                                    )

        employee_server = BedrockAgentCoreRuntime(self, "EmployeeServerAgentCore",
                                                  repository=employee_server_image.repo.repository_uri_for_tag("latest"), protocol="MCP")

        employee_server.node.add_dependency(employee_server_image)

        aws_cdk.CfnOutput(self, "agentRuntimeArn", value=employee_server.resource.ref)


app = aws_cdk.App()

BedrockAgentCoreStack(app, "BedrockAgentCoreStack")

app.synth()
