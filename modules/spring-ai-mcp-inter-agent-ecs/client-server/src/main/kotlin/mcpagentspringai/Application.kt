package mcpagentspringai

import io.modelcontextprotocol.client.McpSyncClient
import org.springframework.ai.chat.client.ChatClient
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider
import org.springframework.ai.tool.annotation.Tool
import org.springframework.ai.tool.annotation.ToolParam
import org.springframework.ai.tool.method.MethodToolCallbackProvider
import org.springframework.ai.tool.resolution.ToolCallbackResolver
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.context.support.GenericApplicationContext
import org.springframework.stereotype.Service


@SpringBootApplication
class Application {

    // Manually create the ToolCallbackResolver to avoid circular dependencies
    @Bean
    fun toolCallbackResolver(applicationContext: GenericApplicationContext): ToolCallbackResolver =
        ActuallyDelegatingToolCallbackResolver(applicationContext)

    // Bedrock Converse chat client with employee database MCP client
    @Bean
    fun chatClient(mcpSyncClients: List<McpSyncClient>, builder: ChatClient.Builder): ChatClient =
        builder
            .defaultToolCallbacks(SyncMcpToolCallbackProvider(mcpSyncClients))
            .build()

    // Expose the tool that uses the chat client as an MCP server
    @Bean
    fun mcpTools(myTools: MyTools): MethodToolCallbackProvider =
        MethodToolCallbackProvider.builder().toolObjects(myTools).build()

}

@Service
class MyTools(val chatClient: ChatClient) {

    @Tool(description = "answers questions related to our employees")
    fun employeeQueries(@ToolParam(description = "the query about the employees", required = true) query: String): String? = run {
        chatClient
            .prompt()
            .system("abbreviate first names with first letter and a period")
            .user(query)
            .call()
            .content()
    }

}

fun main(args: Array<String>) {
    runApplication<Application>(*args)
}
