# Building AI Agents with Embabel: A Spring Developer's Journey from Chat to Autonomous Systems

This document is my exploration of the Embabel framework and how it differs from Spring AI.

## Key Insights

I tried using the same configuration from Spring AI with Embabel and it didn't work. The models that Spring AI uses are registered differently in Embabel's world. This revealed the difference with Embabel: it's not just a wrapper around Spring AI. It's a complete agent framework that happens to use Spring AI as one of its building blocks.

## What Makes Embabel Different

Traditional Spring AI applications follow a request-response pattern:
```kotlin
// Standard Spring AI approach
chatClient.prompt("Tell me about employees with React skills")
    .call()
    .content()
```

Embabel flips this on its head. Instead of imperative API calls, you define agents with goals:
```kotlin
@Agent
class EmployeeQueryAgent {
    @Action
    @AchievesGoal("answer_employee_questions")
    fun findEmployees(criteria: EmployeeCriteria): List<Employee> {
        // The framework handles the AI interactions
    }
}
```

The framework then uses Goal-Oriented Action Planning (GOAP) to figure out how to achieve what you want. It's the difference between telling an intern every single step versus giving them a goal and letting them figure it out.

## The Embabel Architecture Difference

### 1. How Embabel Discovers Models

Embabel uses Spring's dependency injection system to discover AI models, but with a twist. Each model provider (Bedrock, Ollama, Docker) registers models as Spring beans, but only if properly configured.

The `BedrockModels` configuration class (found at `embabel-agent-api/src/main/kotlin/com/embabel/agent/config/models/BedrockModels.kt`) revealed the secret:

```kotlin
if (bedrockProperties.models.isEmpty()) {
    logger.warn("No Bedrock models available.")
    return  // No models registered!
}
```

Without explicit model configuration, the class simply exits without registering anything. This is why Spring AI could see the models but Embabel couldn't.

### 2. The Configuration Revelation

The fix was to create an `application-bedrock.yml` file:

```yaml
embabel:
  models:
    bedrock:
      models:
        - name: us.anthropic.claude-sonnet-4-20250514-v1:0
          knowledge-cutoff: 2025-03-01
          input-price: 3.0
          output-price: 15.0
```

Why does Embabel need this when Spring AI doesn't? Because Embabel isn't just calling models - it's managing them. The framework needs to know:
- Which models are available for different purposes (cheap vs. powerful)
- Cost information for optimizing agent execution
- Knowledge cutoff dates to handle temporal queries correctly

### 3. The Blackboard Pattern in Action

One of Embabel's most elegant features is its use of the Blackboard pattern for state management. In our employee query example:

```kotlin
@Agent
class EmployeeInquiryAgent(
    private val blackboard: Blackboard
) {
    @Action
    fun parseQuery(query: String) {
        val criteria = // ... parse the query
        blackboard.put("search_criteria", criteria)
    }
    
    @Action
    @Requires("search_criteria")
    fun searchEmployees() {
        val criteria = blackboard.get("search_criteria", EmployeeCriteria::class)
        // ... perform search
    }
}
```

Actions communicate through the blackboard, making complex workflows manageable and testable.

## Setting Up Your Own Embabel Project

### Step 1: Project Structure

Start with a standard Spring Boot project and add the Embabel dependencies:

```xml
<dependency>
    <groupId>com.embabel</groupId>
    <artifactId>embabel-agent-spring-boot-starter</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</dependency>
```

### Step 2: The Critical Configuration

Here's what I learned the hard way - you need THREE configuration files for AWS Bedrock:

1. **application.properties** - Your model selection:
```properties
embabel.models.default-llm=us.anthropic.claude-sonnet-4-20250514-v1:0
embabel.models.llms.best=us.anthropic.claude-sonnet-4-20250514-v1:0
embabel.models.llms.cheapest=us.anthropic.claude-sonnet-4-20250514-v1:0
spring.profiles.active=bedrock
```

2. **application-bedrock.yml** - The model registry (this is what I was missing!):
```yaml
spring:
  ai:
    bedrock:
      aws:
        region: ${AWS_REGION}

embabel:
  models:
    bedrock:
      models:
        - name: us.anthropic.claude-sonnet-4-20250514-v1:0
          knowledge-cutoff: 2025-03-01
          input-price: 3.0
          output-price: 15.0
```

3. **Environment Variables** - AWS credentials:
```bash
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1
```

### Step 3: Building Your First Agent

To build an agent with Embabel in this project, you'll work with the MCP-integrated agent architecture. Here's how it's structured:

1. **The Main Agent Class** - See `client/src/main/kotlin/mcpagentspringai/Application.kt:42-86`
   - The `McpEmployeeAgent` is annotated with `@Agent` to mark it as an Embabel agent
   - It uses `@AchievesGoal("answer_employee_questions")` to define its purpose
   - The agent integrates with MCP tools through Spring AI's client capabilities

2. **Key Components**:
   - **ModelProvider Integration**: The agent uses Embabel's `ModelProvider` to access the configured LLM (see line 44)
   - **MCP Tool Integration**: Spring AI's `ChatClient` is configured with MCP tools from the server (see lines 54-58)
   - **Goal-Oriented Design**: The `processInquiry` method is marked as an `@Action` that achieves the defined goal

3. **MCP Server Tools** - See `server/src/main/kotlin/embabelagent/Application.kt:137-165`
   - The server exposes tools like `searchEmployees`, `getEmployeeById`, and `aggregateBySkill`
   - These tools are automatically discovered and made available to the agent through MCP

4. **Configuration Requirements**:
   - Model configuration in `client/src/main/resources/application.properties` (lines 1-4)
   - Bedrock profile configuration in `client/src/main/resources/application-bedrock.yml`
   - MCP server URL configuration pointing to the employee data service

5. **Running the Agent**:
   - Start the MCP server first: `./mvnw -pl server spring-boot:run`
   - Run the client agent: `./run-client.sh` (handles AWS credential export)
   - The agent will connect to the MCP server and use its tools to answer employee queries

## The Execution Modes That Change Everything

Embabel offers three ways to run agents, each suited for different scenarios:

### Focused Mode (When You Know What You Want)
```kotlin
platform.focused(McpEmployeeAgent::class)
    .goal("answer_employee_questions")
    .set("question", "Find React developers")
    .execute()
```

### Closed Mode (When You Have Multiple Agents)
```kotlin
platform.closed()
    .intent("I need to find senior React developers in our team")
    .execute()
// The platform figures out which agent to use
```

### Open Mode (Full Autonomous Operation)
```kotlin
platform.open()
    .observe("New requirement for React expertise posted")
    .execute()
// The platform determines both the goal AND the agent
```

## Lessons Learned and Best Practices

1. **Always Define Your Models Explicitly**: Unlike Spring AI, Embabel requires complete model definitions. This isn't a limitation - it's a feature that enables intelligent model selection.

2. **Think in Goals, Not Steps**: Design your agents around what they achieve, not how they achieve it. Let the GOAP planner handle the sequencing.

3. **Use the Blackboard**: Don't pass data between actions through method calls. The blackboard pattern makes your agents more flexible and testable.

4. **Profile Your Configurations**: Use Spring profiles to separate concerns:
   ```
   application-bedrock.yml    # AWS Bedrock models
   application-ollama.yml     # Local Ollama models  
   application-dev.yml        # Development overrides
   ```

5. **Monitor Your Costs**: With model pricing configured, Embabel can help you optimize costs:
   ```kotlin
   @Action
   @PreferModel(selection = ModelSelection.CHEAPEST)
   fun initialScreening(query: String) {
       // Use cheaper model for simple tasks
   }
   
   @Action
   @PreferModel(selection = ModelSelection.BEST)
   fun complexAnalysis(data: ComplexData) {
       // Use powerful model when needed
   }
   ```

## The MCP Integration Pattern

While this architecture might look like any MCP agent project at first glance, Embabel fundamentally transforms how MCP tools are utilized:

```
┌─────────────────┐     MCP/SSE      ┌──────────────────┐
│   MCP Client    │ ←-------------→  │   MCP Server     │
│ (Embabel Agent) │                  │ (Employee Data)  │
└─────────────────┘                  └──────────────────┘
        ↓                                     ↓
   AWS Bedrock                          Employee DB
   + GOAP Planner                       
   + Blackboard
```

**What Makes This Different:**

1. **Goal-Oriented vs Tool-Oriented**: Standard MCP agents directly invoke tools based on user requests. Embabel agents define goals and let the GOAP planner determine which MCP tools to use and in what sequence.

2. **Dynamic Planning**: Instead of hardcoded tool invocation logic, Embabel evaluates the current state, determines the goal state, and uses A* pathfinding to find the optimal sequence of actions (including MCP tool calls).

3. **Stateful Execution**: The Blackboard pattern maintains context across multiple MCP tool invocations, enabling complex multi-step workflows that standard MCP agents struggle with.

4. **Tool Abstraction**: MCP tools become actions within Embabel's planning system. The agent doesn't just call `searchEmployees` - it understands that this action helps achieve the goal of "answer_employee_questions" and can combine it with other actions as needed.

In essence, Embabel transforms MCP from a tool invocation protocol into a capability layer for autonomous goal-oriented agents.

**Example Scenario**: "Find the top 3 React developers and check if they're available for a new project"

*Standard MCP Agent:*
- Hardcoded sequence: searchEmployees → filter by React → sort by experience → check availability
- If any step fails or needs adjustment, the entire flow must be rewritten

*Embabel+MCP Agent:*
- Defines goal: "identify_available_react_experts"
- GOAP planner determines optimal action sequence based on available MCP tools
- If `checkAvailability` tool is down, it might adapt by using `getEmployeeById` with status checks
- Blackboard maintains context (found developers, skill levels) across all tool invocations

## Summary

This document explored the key differences between Spring AI and Embabel, revealing that Embabel is a complete agent framework that uses Spring AI as a building block rather than just another AI wrapper. 

**Key Lessons Learned:**

1. **Explicit Model Configuration**: Unlike Spring AI, Embabel requires complete model definitions in configuration files to enable intelligent model selection and cost optimization.

2. **Goal-Oriented Architecture**: Embabel uses Goal-Oriented Action Planning (GOAP) where you define what agents should achieve, not how they should achieve it.

3. **Blackboard Pattern**: Agents communicate through a shared blackboard for state management, making complex workflows more manageable and testable.

4. **Multiple Execution Modes**: Embabel provides focused, closed, and open modes for different levels of agent autonomy.

5. **MCP Integration**: The project demonstrates effective integration between MCP for service communication and Embabel for AI orchestration.

The framework's complexity serves a purpose - it enables building autonomous agents that can plan, execute, and adapt based on defined goals rather than imperative step-by-step instructions.

## Important Notes for LLMs: Infrastructure Setup

When copying infrastructure from other projects (especially CloudFormation templates and deployment scripts), be extremely careful to ensure ALL components are properly adapted:

### Common Pitfalls to Avoid:

1. **CloudFormation Parameter Mismatch**:
   - Deployment scripts often pass parameters that must exist in the CloudFormation template
   - Example: `ClientStartupDelay`, `ServerImageTag`, `ClientImageTag` parameters
   - Always verify that parameters used in scripts match those defined in templates

2. **CloudFormation Output Dependencies**:
   - Scripts may depend on specific stack outputs (e.g., `ServerServiceName`, `ClientServiceName`)
   - Never remove outputs without checking if deployment scripts reference them
   - Use grep to search for output names in all scripts before removing

3. **Service Dependencies**:
   - Don't remove `DependsOn` attributes without understanding the startup order requirements
   - MCP servers must start before clients that connect to them

4. **Model-Specific Permissions**:
   - Different frameworks use different AI models
   - Update IAM permissions in base.cfn to match the actual models used
   - Spring AI might use Nova, while Embabel uses Claude and Cohere

5. **Hardcoded vs Parameterized Values**:
   - Check for hardcoded values that should be parameters
   - Container image tags should use parameters, not hardcoded `:latest`
   - Service counts should reference parameters for flexible deployment

### Verification Checklist:

Before deploying copied infrastructure:
1. ✓ Compare ALL parameters between CloudFormation templates and deployment scripts
2. ✓ Verify all CloudFormation outputs are present that scripts expect
3. ✓ Check that container names match between templates and any references
4. ✓ Ensure IAM permissions match the actual services/models being used
5. ✓ Test deployment scripts match the CloudFormation template structure
6. ✓ Verify resource naming conventions are consistently updated

### Example Issue We Encountered:
```bash
# The deploy script passed these parameters:
--params BaseStackName=embabel-agent-base,ClientStartupDelay=0,ClientImageTag=bf9a80e,ServerImageTag=bf9a80e

# But the CloudFormation template only had:
Parameters:
  BaseStackName:
    Type: String
    Default: embabel-agent-base
    Description: Name of the base infrastructure stack
# Missing: ServerImageTag, ClientImageTag, ClientStartupDelay
```

This mismatch caused deployment failures that required careful debugging to identify and fix.

