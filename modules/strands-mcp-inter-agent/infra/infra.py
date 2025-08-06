import aws_cdk

from aws_cdk import (
    aws_cognito
)

from constructs import Construct

from buildpack_image_asset import BuildpackImageAsset
from bedrock_agentcore_runtime import BedrockAgentCoreRuntime


class BedrockAgentCoreStack(aws_cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        user_pool = aws_cognito.UserPool(self, "UserPool",
                                         password_policy=aws_cognito.PasswordPolicy(
                                             min_length=8
                                         ),
                                         removal_policy=aws_cdk.RemovalPolicy.DESTROY
                                         )

        user_pool_client = aws_cognito.UserPoolClient(self, "UserPoolClient",
                                                      user_pool=user_pool,
                                                      generate_secret=False,
                                                      auth_flows=aws_cognito.AuthFlow(
                                                          user_password=True,
                                                      ),
                                                      )

        employee_server_image = BuildpackImageAsset(self, "EmployeeServerImage",
                                                    source_path="./",
                                                    builder="public.ecr.aws/heroku/builder:24",
                                                    run_image="public.ecr.aws/heroku/heroku:24",
                                                    platform="linux/amd64",
                                                    default_process="employee-server",
                                                    )

        employee_server = BedrockAgentCoreRuntime(self, "EmployeeServerAgentCore",
                                                  repository=employee_server_image.ecr_repo,
                                                  protocol="MCP",
                                                  # discovery_url=f"https://cognito-idp.{self.region}.amazonaws.com/{user_pool.user_pool_id}/.well-known/openid-configuration",
                                                  # client_id=user_pool_client.user_pool_client_id
                                                  )

        employee_server.node.add_dependency(employee_server_image)

        # todo: reuse same container image but requires a way to specify the cmd/entrypoint in agentcore runtime

        employee_agent_image = BuildpackImageAsset(self, "EmployeeAgentImage",
                                                    source_path="./",
                                                    builder="public.ecr.aws/heroku/builder:24",
                                                    run_image="public.ecr.aws/heroku/heroku:24",
                                                    platform="linux/amd64",
                                                    default_process="employee-agent",
                                                    )

        employee_agent = BedrockAgentCoreRuntime(self, "EmployeeAgentAgentCore",
                                                 repository=employee_agent_image.ecr_repo,
                                                 protocol="MCP",
                                                 # discovery_url=f"https://cognito-idp.{self.region}.amazonaws.com/{user_pool.user_pool_id}/.well-known/openid-configuration",
                                                 # client_id=user_pool_client.user_pool_client_id,
                                                 env={
                                                     "EMPLOYEE_INFO_ARN": employee_server.resource.ref
                                                 }
                                                 )

        employee_agent.node.add_dependency(employee_agent_image)

        hr_agent_image = BuildpackImageAsset(self, "HRAgentImage",
                                                   source_path="./",
                                                   builder="public.ecr.aws/heroku/builder:24",
                                                   run_image="public.ecr.aws/heroku/heroku:24",
                                                   platform="linux/amd64",
                                                   default_process="hr-agent",
                                                   )

        hr_agent = BedrockAgentCoreRuntime(self, "HRAgentAgentCore",
                                             repository=hr_agent_image.ecr_repo,
                                             protocol="HTTP",
                                             env={
                                                 "EMPLOYEE_AGENT_URL": f"https://bedrock-agentcore.{self.region}.amazonaws.com/runtimes/{employee_agent.resource.ref.replace(':', '%3A').replace('/', '%2F')}/invocations?qualifier=DEFAULT"
                                             }
                                             )

        hr_agent.node.add_dependency(hr_agent_image)

        aws_cdk.CfnOutput(self, "PoolId", value=user_pool.user_pool_id)
        aws_cdk.CfnOutput(self, "ClientId", value=user_pool_client.user_pool_client_id)

        aws_cdk.CfnOutput(self, "EmployeeServerAgentRuntimeArn", value=employee_server.resource.ref)
        aws_cdk.CfnOutput(self, "EmployeeAgentAgentRuntimeArn", value=employee_agent.resource.ref)
        aws_cdk.CfnOutput(self, "HRAgentAgentRuntimeArn", value=hr_agent.resource.ref)


app = aws_cdk.App()

BedrockAgentCoreStack(app, "BedrockAgentCoreStack")

app.synth()
