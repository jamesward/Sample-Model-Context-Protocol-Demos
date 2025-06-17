package mcpagentspringai

import com.embabel.agent.api.annotation.AchievesGoal
import com.embabel.agent.api.annotation.Action
import com.embabel.agent.api.annotation.Agent
import com.embabel.agent.api.annotation.usingDefaultLlm
import com.embabel.agent.api.common.autonomy.Autonomy
import com.embabel.agent.api.common.createObject
import com.embabel.agent.core.ToolGroup
import com.embabel.agent.core.ToolGroupDescription
import com.embabel.agent.core.ToolGroupPermission
import com.embabel.agent.domain.io.UserInput
import com.embabel.agent.domain.library.HasContent
import com.embabel.agent.tools.mcp.McpToolGroup
import com.embabel.common.ai.model.EmbeddingService
import com.fasterxml.jackson.annotation.JsonClassDescription
import com.fasterxml.jackson.databind.annotation.JsonDeserialize
import io.modelcontextprotocol.client.McpSyncClient
import org.springframework.ai.bedrock.cohere.BedrockCohereEmbeddingModel
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.context.properties.ConfigurationPropertiesScan
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController


@SpringBootApplication(scanBasePackageClasses = [com.embabel.agent.AgentApplication::class, Application::class])
@ConfigurationPropertiesScan(basePackageClasses = [com.embabel.agent.AgentApplication::class, Application::class])
open class Application {
    @Bean
    open fun embeddingService(bedrockCohereEmbeddingModel: BedrockCohereEmbeddingModel): EmbeddingService =
        EmbeddingService(
            name = "cohere.embed-english-v3",
            provider = "bedrock-cohere",
            model = bedrockCohereEmbeddingModel
        )

    @Bean
    open fun employeeToolGroup(mcpSyncClients: List<McpSyncClient>): ToolGroup = McpToolGroup(
        description = ToolGroupDescription(description = "Employee Tool Group", role = "integration"),
        provider = "remote",
        name = "employee",
        permissions = setOf(ToolGroupPermission.INTERNET_ACCESS),
        clients = mcpSyncClients,
        filter = { true }
    )
}

@JsonClassDescription("Employee and their skills")
@JsonDeserialize
data class Employee(val name: String, val skills: List<String>)

@JsonClassDescription("List of employees")
@JsonDeserialize
data class Employees(val employees: List<Employee>)

data class Writeup(override val content: String) : HasContent

@Agent(description = "Employee Info Agent")
class EmployeeAgent {

    @Action(toolGroups = ["integration"])
    fun lookupEmployees(userInput: UserInput): Employees =
        usingDefaultLlm.createObject(userInput.content)

    @AchievesGoal("queries the employees")
    @Action
    fun queryEmployeeData(employees: Employees): Writeup =
        usingDefaultLlm.createObject("""
            Display the following list of employees in a nice way:
            $employees
        """.trimIndent())

}

data class Prompt(val question: String)

@RestController
class ConversationalController(val autonomy: Autonomy) {
    @PostMapping("/inquire")
    fun inquire(@RequestBody prompt: Prompt): String =
        autonomy.chooseAndRunAgent(prompt.question).output.toString()
}

fun main(args: Array<String>) {
    runApplication<Application>(*args)
}
