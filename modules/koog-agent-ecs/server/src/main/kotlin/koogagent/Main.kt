package koogagent

import io.ktor.server.cio.CIO
import io.ktor.server.engine.embeddedServer
import io.modelcontextprotocol.kotlin.sdk.CallToolResult
import io.modelcontextprotocol.kotlin.sdk.Implementation
import io.modelcontextprotocol.kotlin.sdk.ServerCapabilities
import io.modelcontextprotocol.kotlin.sdk.TextContent
import io.modelcontextprotocol.kotlin.sdk.Tool
import io.modelcontextprotocol.kotlin.sdk.server.Server
import io.modelcontextprotocol.kotlin.sdk.server.ServerOptions
import io.modelcontextprotocol.kotlin.sdk.server.mcp
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.encodeToJsonElement
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.put
import kotlinx.serialization.json.putJsonObject

@Serializable
data class Employee(val name: String, val skills: List<String>)

val getSkillsTool: Tool = Tool(
    name = "get skills",
    description = "employees have skills. this returns all possible skills our employees have",
    inputSchema = Tool.Input(),
    outputSchema = Tool.Output(
        buildJsonObject {
            putJsonObject("skills") {
                put("type", "array")
                put("description", "employee skills")
            }
        }
    ),
    annotations = null,
)

val getEmployeesBySkill: Tool = Tool(
    name = "get employees by skill",
    description = "this returns all employees with a specific skill",
    inputSchema = Tool.Input(
        buildJsonObject {
            putJsonObject("skill") {
                put("type", "string")
                put("description", "skill to filter employees by")
            }
        }
    ),
    outputSchema = Tool.Output(
        buildJsonObject {
            putJsonObject("employees") {
                put("type", "array")
                put("description", "employees")
                // todo: items for employee type
            }
        }
    ),
    annotations = null,
)

fun main(args: Array<String>) {
    val port = args.getOrNull(1)?.toIntOrNull() ?: 8081

    val mcpServer = Server(
        serverInfo = Implementation(
            name = "employee data",
            version = "1.0.0"
        ),
        options = ServerOptions(
            capabilities = ServerCapabilities(
                logging = null,
                tools = ServerCapabilities.Tools(false)
            )
        )
    )

    mcpServer.addTool(getSkillsTool) {
        val skills = Json.encodeToJsonElement(SampleData.employees.flatMap { it.skills }.toSet())
        CallToolResult(
            content = emptyList(),
            structuredContent = buildJsonObject { put("skills", skills) }
        )
    }

    mcpServer.addTool(getEmployeesBySkill) { request ->
        request.arguments["skill"]?.jsonPrimitive?.content?.let { skill ->
            val employees = SampleData.employees.filter { employee ->
                employee.skills.any { it.equals(skill, ignoreCase = true) }
            }

            CallToolResult(
                content = emptyList(),
                structuredContent = buildJsonObject { put("employees", Json.encodeToJsonElement(employees)) }
            )
        } ?: CallToolResult(
            content = listOf(TextContent("Skill must be provided")),
            isError = true,
        )
    }

    val server = embeddedServer(CIO, port = port) {
        mcp {
            mcpServer
        }
    }

    server.start(wait = true)
}
