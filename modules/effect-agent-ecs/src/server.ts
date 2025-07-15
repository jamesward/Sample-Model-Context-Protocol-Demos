import {AiTool, AiToolkit, McpServer} from "@effect/ai"
import {NodeHttpServer, NodeRuntime} from "@effect/platform-node"
import {Effect, Layer, Schema} from "effect"
import {createServer} from "node:http"
import {HttpRouter} from "@effect/platform"
import {employees, EmployeeSchema} from "./sample-data";

export const employeesToolkit =
  AiToolkit.make(
    AiTool.make("get_skills", {
      description:
        "all of the skills that employees may have - use this list to figure out related skills",
      success: Schema.Struct({
        skills: Schema.Array(Schema.String)
      })
    }),
    AiTool.make("get_employees_with_skill", {
      description:
        "employees that have a specified skill - output includes fullname (First Last) and their skills",
      parameters: {
        skill: Schema.String.annotations({
          description: "employee skill",
        }),
      },
      success: Schema.Struct({
        employees: Schema.Array(EmployeeSchema)
      })
    })
  )

export const employeesToolkitHandlers = employeesToolkit.of({
  get_skills: () => Effect.gen(function*(){
    yield* Effect.log("get skills");
    return {
      skills: Array.from(new Set(employees.flatMap(employee => employee.skills)))
    }
  }),
  get_employees_with_skill: (params) => Effect.gen(function*(){
    yield* Effect.log(`get employee with ${params.skill} skills`);
    return {
      employees: employees.filter(employee =>
        employee.skills.some(empSkill =>
          empSkill.toLowerCase() === params.skill.toLowerCase()
        )
      )
    }
  })
})

export const employeeToolkitLayer = employeesToolkit.toLayer(
  Effect.succeed(employeesToolkitHandlers)
)

const EmployeeTools = McpServer.toolkit(employeesToolkit).pipe(Layer.provide(employeeToolkitLayer))


const ServerLayer = Layer.mergeAll(
  EmployeeTools,
  HttpRouter.Default.serve()
).pipe(
  Layer.provide(McpServer.layerHttp({
    name: "employee-info",
    version: "1.0.0",
    path: "/mcp"
  })),
  Layer.provide(NodeHttpServer.layer(createServer, { port: 3000 }))
)

Layer.launch(ServerLayer).pipe(NodeRuntime.runMain)
