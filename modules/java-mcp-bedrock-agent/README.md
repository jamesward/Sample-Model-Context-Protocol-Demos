# Sample: MCP Agent with Bedrock

> A multi-turn agent using Amazon Bedrock Converse and the MCP Java SDK

```mermaid
sequenceDiagram
    participant User
    participant Application
    participant McpClient
    participant BedrockRuntimeClient
    participant McpServer
    participant BedrockService

    Note over Application: Application starts with a query
    
    Application->>McpClient: initialize()
    McpClient->>McpServer: HTTP request for initialization
    McpServer-->>McpClient: Return server info
    
    Application->>McpClient: listTools()
    McpClient->>McpServer: HTTP request for tools
    McpServer-->>McpClient: Return available tools
    
    Application->>Application: mcpToolsToConverseTools(tools)
    Note over Application: Convert MCP tools to Bedrock Converse tools format
    
    Application->>BedrockRuntimeClient: create client
    
    loop Conversation Loop
        Application->>BedrockRuntimeClient: converse(request)
        BedrockRuntimeClient->>BedrockService: Send converse request
        BedrockService-->>BedrockRuntimeClient: Return response
        BedrockRuntimeClient-->>Application: Return response
        
        Application->>User: Display text response
        
        alt stopReason == TOOL_USE
            Note over Application: Model wants to use a tool
            
            Application->>Application: Extract tool use details
            Application->>McpClient: callTool(request)
            McpClient->>McpServer: HTTP request to call tool
            McpServer-->>McpClient: Return tool result
            McpClient-->>Application: Return tool result
            
            Application->>Application: Create tool result message
            Application->>Application: Add to messages array
            Note over Application: Continue conversation loop
        else stopReason == END_TURN
            Note over Application: Conversation complete
            Application->>Application: Break loop
        end
    end
```

## Setup

1. Setup Bedrock in the AWS Console, [request access to Nova Lite](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)
1. [Setup auth for local development](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-authentication.html)

## Run The Agent

```
./mvnw compile exec:java
```

Resources:
- https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/java_bedrock-runtime_code_examples.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-inference-call.html
