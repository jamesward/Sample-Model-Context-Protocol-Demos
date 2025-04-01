package mcpagentspringai

import org.springframework.ai.tool.annotation.Tool
import org.springframework.ai.tool.annotation.ToolParam
import org.springframework.ai.tool.method.MethodToolCallbackProvider
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.stereotype.Service

@SpringBootApplication
class Application {
    @Bean
    fun mcpTools(myTools: MyTools): MethodToolCallbackProvider =
        MethodToolCallbackProvider.builder().toolObjects(myTools).build()
}

data class Employee(val name: String, val skills: List<String>)

@Service
class MyTools {

    @Tool(description = "employees have skills. this returns all possible skills our employees have")
    fun getSkills(): Set<String> =
        SampleData.employees.flatMap { it.skills }.toSet()

    @Tool(description = "get the employees that have a specific skill")
    fun getEmployeesWithSkill(@ToolParam(description = "skill") skill: String): List<Employee> =
        SampleData.employees.filter { employee ->
            employee.skills.any { it.equals(skill, ignoreCase = true) }
        }

}

fun main(args: Array<String>) {
    SampleData.employees.forEach { println(it) }
    runApplication<Application>(*args)
}
