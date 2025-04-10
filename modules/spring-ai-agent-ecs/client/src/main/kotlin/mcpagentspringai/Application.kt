package mcpagentspringai

import io.modelcontextprotocol.client.McpSyncClient
import org.springframework.ai.chat.client.ChatClient
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController

@SpringBootApplication
class Application {
    @Bean
    fun chatClient(mcpSyncClients: List<McpSyncClient>, builder: ChatClient.Builder): ChatClient {
        return builder
            .defaultTools(SyncMcpToolCallbackProvider(mcpSyncClients))
            .build()
    }
}

data class Prompt(val question: String)

@RestController
class ConversationalController(val chatClient: ChatClient) {

    @PostMapping("/inquire")
    fun inquire(@RequestBody prompt: Prompt): String =
        chatClient
                .prompt()
                .user(prompt.question)
                .call()
                .content() ?: "Please try again later."
}


fun main(args: Array<String>) {
    runApplication<Application>(*args)
}
