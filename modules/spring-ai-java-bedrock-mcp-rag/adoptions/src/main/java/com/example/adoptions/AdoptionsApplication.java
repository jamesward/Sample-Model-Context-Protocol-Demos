package com.example.adoptions;

import io.modelcontextprotocol.client.McpSyncClient;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.vectorstore.QuestionAnswerAdvisor;
import org.springframework.ai.chat.client.advisor.vectorstore.VectorStoreChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.annotation.Id;
import org.springframework.data.repository.ListCrudRepository;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.List;

/**
 * @author James Ward
 * @author Josh Long
 */
@SpringBootApplication
public class AdoptionsApplication {
    public static void main(String[] args) {
        SpringApplication.run(AdoptionsApplication.class, args);
    }
}

@Configuration
class ConversationalConfiguration {

    @Bean
    ChatClient chatClient(
            List<McpSyncClient> mcpSyncClients,
            ChatClient.Builder builder,
            VectorStore vectorStore) {

        var system = """
                You are an AI powered assistant to help people adopt a dog from the adoption\s
                agency named Pooch Palace with locations in Atlanta, Antwerp, Seoul, Tokyo, Singapore, Paris,\s
                Mumbai, New Delhi, Barcelona, San Francisco, and London. Information about the dogs available\s
                will be presented below. If there is no information, then return a polite response suggesting we\s
                don't have any dogs available.
                
                If the response involves a timestamp, be sure to convert it to something human-readable.
                
                Do _not_ include any indication of what you're thinking. Nothing should be sent to the client between <thinking> tags.
                Just give the answer.
                """;

        return builder
                .defaultSystem(system)
                .defaultToolCallbacks(new SyncMcpToolCallbackProvider(mcpSyncClients))
                .defaultAdvisors(VectorStoreChatMemoryAdvisor.builder(vectorStore).build())
                .build();
    }

}

interface DogRepository extends ListCrudRepository<Dog, Integer> {
}

record Dog(@Id int id, String name, String owner, String description) {
}


@Controller
@ResponseBody
class ConversationalController {

    private final ChatClient chatClient;
    private final QuestionAnswerAdvisor questionAnswerAdvisor;

    ConversationalController(VectorStore vectorStore, ChatClient chatClient) {
        this.chatClient = chatClient;
        this.questionAnswerAdvisor = new QuestionAnswerAdvisor(vectorStore);
    }

    @PostMapping("/{id}/inquire")
    String inquire(@PathVariable String id, @RequestParam String question) {
        return chatClient
                .prompt()
                .user(question)
                .advisors(questionAnswerAdvisor)
                .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, id))
                .call()
                .content();
    }
}
