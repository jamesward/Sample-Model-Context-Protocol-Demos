package mcpagentspringai

import io.modelcontextprotocol.client.McpSyncClient
import org.slf4j.LoggerFactory
import org.springframework.ai.chat.client.ChatClient
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController
import jakarta.annotation.PostConstruct
import org.springframework.beans.factory.annotation.Value


@SpringBootApplication
class Application {
    private val logger = LoggerFactory.getLogger(Application::class.java)
    
    @Value("\${MCP_SERVICE_URL:http://localhost:8081}")
    private lateinit var mcpServiceUrl: String
    
    @Value("\${spring.ai.bedrock.aws.region:us-east-1}")
    private lateinit var awsRegion: String
    
    @Value("\${spring.ai.bedrock.nova.chat.model:nova-pro-v1:0}")
    private lateinit var bedrockModel: String
    
    @PostConstruct
    fun logStartup() {
        logger.info("=== MCP Client/Agent Application Starting ===")
        logger.info("MCP Service URL: $mcpServiceUrl")
        logger.info("AWS Region: $awsRegion")
        logger.info("Bedrock Model: $bedrockModel")
    }
    
    @Bean
    fun chatClient(mcpSyncClients: List<McpSyncClient>, builder: ChatClient.Builder): ChatClient {
        logger.info("Configuring ChatClient with ${mcpSyncClients.size} MCP client(s)")
        return builder
            .defaultToolCallbacks(SyncMcpToolCallbackProvider(mcpSyncClients))
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
