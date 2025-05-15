package mcpagentspringai;

import io.modelcontextprotocol.client.McpSyncClient;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

@Configuration
class ConversationalConfiguration {
    @Bean
    ChatClient chatClient(List<McpSyncClient> mcpSyncClients, ChatClient.Builder builder) {
        return builder
                .defaultToolCallbacks(new SyncMcpToolCallbackProvider(mcpSyncClients))
                .build();
    }
}

record Prompt(String question) { }

@RestController
class ConversationalController {

    private final ChatClient chatClient;

    ConversationalController(ChatClient chatClient) {
        this.chatClient = chatClient;
    }

    @PostMapping("/inquire")
    String inquire(@RequestBody Prompt prompt) {
        return chatClient
                .prompt()
                .user(prompt.question())
                .call()
                .content();
    }
}
