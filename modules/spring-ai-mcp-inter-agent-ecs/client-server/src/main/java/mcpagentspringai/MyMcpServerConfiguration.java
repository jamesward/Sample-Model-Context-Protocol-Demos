package mcpagentspringai;

import io.modelcontextprotocol.server.McpServerFeatures;
import io.modelcontextprotocol.server.McpSyncServer;
import io.modelcontextprotocol.server.McpSyncServerExchange;
import io.modelcontextprotocol.spec.McpSchema;
import io.modelcontextprotocol.spec.McpServerTransportProvider;
import org.springframework.ai.mcp.server.autoconfigure.McpServerAutoConfiguration;
import org.springframework.ai.mcp.server.autoconfigure.McpServerProperties;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;
import java.util.function.BiConsumer;

// this enables creating an MCP server which doesn't have the MCP client's tools
@Configuration
@EnableConfigurationProperties(McpServerProperties.class)
public class MyMcpServerConfiguration {

    @Bean
    @ConditionalOnProperty(name = "spring.ai.mcp.server.enabled", havingValue = "true")
    McpSyncServer mcpSyncServer(McpServerTransportProvider transportProvider,
                                McpServerProperties serverProperties,
                                ObjectProvider<List<McpServerFeatures.SyncToolSpecification>> tools,
                                ObjectProvider<List<McpServerFeatures.SyncResourceSpecification>> resources,
                                ObjectProvider<List<McpServerFeatures.SyncPromptSpecification>> prompts,
                                ObjectProvider<List<McpServerFeatures.SyncCompletionSpecification>> completions,
                                ObjectProvider<BiConsumer<McpSyncServerExchange, List<McpSchema.Root>>> rootsChangeConsumers) {

        return (new McpServerAutoConfiguration()).mcpSyncServer(transportProvider, McpSchema.ServerCapabilities.builder(), serverProperties, tools, resources, prompts, completions, rootsChangeConsumers, List.of());
    }

}
