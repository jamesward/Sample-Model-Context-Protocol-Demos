package mcpagentspringai

import org.springframework.ai.tool.ToolCallback
import org.springframework.ai.tool.ToolCallbackProvider
import org.springframework.ai.tool.resolution.SpringBeanToolCallbackResolver
import org.springframework.ai.tool.resolution.StaticToolCallbackResolver
import org.springframework.ai.tool.resolution.ToolCallbackResolver
import org.springframework.beans.factory.getBeansOfType
import org.springframework.context.support.GenericApplicationContext
import org.springframework.util.Assert
import kotlin.concurrent.atomics.AtomicBoolean
import kotlin.concurrent.atomics.ExperimentalAtomicApi

@OptIn(ExperimentalAtomicApi::class)
class ActuallyDelegatingToolCallbackResolver(val context: GenericApplicationContext) : ToolCallbackResolver {

    val initialized = AtomicBoolean(false)

    override fun resolve(toolName: String): ToolCallback? {
        val all = mutableListOf<ToolCallbackResolver>()

        if (initialized.compareAndSet(false, true)) {
            val tcbProviders = context.getBeansOfType<ToolCallbackProvider>().values.toList()

            val allFunctionAndToolCallbacks = context.getBeansOfType<ToolCallback>().values.toList()

            val staticToolCallbackResolver = StaticToolCallbackResolver(
                allFunctionAndToolCallbacks + tcbProviders.flatMap { it.toolCallbacks.toList() }
            )

            val springBeanToolCallbackResolver = SpringBeanToolCallbackResolver.builder()
                .applicationContext(context)
                .build()

            Assert.hasText(toolName, "toolName cannot be null or empty")

            all.add(staticToolCallbackResolver)
            all.add(springBeanToolCallbackResolver)
        }

        return all.firstNotNullOfOrNull { it.resolve(toolName) }
    }

}
