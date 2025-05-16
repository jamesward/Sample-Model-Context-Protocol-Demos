package mcpagentspringai;

import io.modelcontextprotocol.client.McpSyncClient;
import io.modelcontextprotocol.server.McpServerFeatures;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.mcp.McpToolUtils;
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;
import org.springframework.ai.mcp.server.autoconfigure.McpServerAutoConfiguration;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Service;

import java.util.List;

@SpringBootApplication(exclude = {McpServerAutoConfiguration.class})
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

@Configuration
class AgentConfiguration {

    // Expose the tool that uses the chat client as an MCP server
    @Bean
    public List<McpServerFeatures.SyncToolSpecification> myToolSpecs(MyTools myTools) {
        var toolCallbacks = List.of(MethodToolCallbackProvider.builder().toolObjects(myTools).build().getToolCallbacks());
        return McpToolUtils.toSyncToolSpecification(toolCallbacks);
    }

    // Bedrock Converse chat client with employee database MCP client
    @Bean
    ChatClient chatClient(List<McpSyncClient> mcpSyncClients, ChatClient.Builder builder) {
        return builder
                .defaultToolCallbacks(new SyncMcpToolCallbackProvider(mcpSyncClients))
                .build();
    }

}

@Service
class EmployeeQueries {
    private final ChatClient chatClient;

    EmployeeQueries(ChatClient chatClient) {
        this.chatClient = chatClient;
    }

    String query(String question) {
        return chatClient
                .prompt()
                .system("abbreviate employee first names with first letter and a period")
                .user(question)
                .call()
                .content();
    }

}

@Service
class MyTools {

    private final EmployeeQueries employeeQueries;

    MyTools(EmployeeQueries employeeQueries) {
        this.employeeQueries = employeeQueries;
    }

    @Tool(description = "answers questions related to our employees")
    String inquire(@ToolParam(description = "the query about the employees", required = true) String question) {
        return employeeQueries.query(question);
    }

}
