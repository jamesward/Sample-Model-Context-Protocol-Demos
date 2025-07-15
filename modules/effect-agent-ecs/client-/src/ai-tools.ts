import { AiTool, AiToolkit } from "@effect/ai";
import { Effect, Schema } from "effect";
import { McpClient } from "./mcp-client.js";

// Define the employee schema
const Employee = Schema.Struct({
  name: Schema.String,
  skills: Schema.Array(Schema.String),
});

// Define the GetSkills tool
const GetSkills = AiTool.make("GetSkills", {
  description: "employees have skills. this returns all possible skills our employees have",
  success: Schema.Array(Schema.String),
  failure: Schema.String,
  parameters: {},
});

// Define the GetEmployeesWithSkill tool
const GetEmployeesWithSkill = AiTool.make("GetEmployeesWithSkill", {
  description: "get the employees that have a specific skill",
  success: Schema.Array(Employee),
  failure: Schema.String,
  parameters: {
    skill: Schema.String.annotations({
      description: "skill to search for",
    }),
  },
});

// Create the toolkit
export class EmployeeToolkit extends AiToolkit.make(
  GetSkills,
  GetEmployeesWithSkill
) {}

// Create the tool handlers layer
export const EmployeeToolHandlers = EmployeeToolkit.toLayer(
  Effect.gen(function* () {
    const mcpClient = yield* McpClient;

    return {
      GetSkills: () =>
        mcpClient.callTool("getSkills").pipe(
          Effect.catchAll((error) => Effect.fail(error.message))
        ),

      GetEmployeesWithSkill: ({ skill }) =>
        mcpClient.callTool("getEmployeesWithSkill", { skill }).pipe(
          Effect.catchAll((error) => Effect.fail(error.message))
        ),
    };
  })
);
