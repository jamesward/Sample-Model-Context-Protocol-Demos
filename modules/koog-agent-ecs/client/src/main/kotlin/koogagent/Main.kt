package koogagent

import ai.koog.agents.core.agent.AIAgent
import ai.koog.agents.mcp.McpToolRegistryProvider
import ai.koog.agents.utils.use
import ai.koog.prompt.executor.llms.all.simpleBedrockExecutor
import ai.koog.prompt.executor.clients.bedrock.BedrockModels


suspend fun main() {
    val employeeDataUrl = System.getenv("EMPLOYEE_DATA_URL") ?: "http://localhost:8081/"

    val transport = McpToolRegistryProvider.defaultSseTransport(employeeDataUrl)

    val toolRegistry = McpToolRegistryProvider.fromTransport(
        transport = transport,
        name = "employee-tools",
        version = "1.0.0"
    )

    AIAgent(
        executor = simpleBedrockExecutor(
            System.getenv("AWS_ACCESS_KEY_ID") ?: throw IllegalArgumentException("AWS_ACCESS_KEY_ID env var is required"),
            System.getenv("AWS_SECRET_ACCESS_KEY") ?: throw IllegalArgumentException("AWS_SECRET_ACCESS_KEY env var is required")
        ),
        llmModel = BedrockModels.AmazonNovaMicro,
        toolRegistry = toolRegistry,
    ).use { agent ->
        val result = agent.run("say to the user: Hello")
        println(result)
    }
}
