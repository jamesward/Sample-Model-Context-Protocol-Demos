import {AmazonBedrockClient, AmazonBedrockLanguageModel} from "@effect/ai-amazon-bedrock"
import {AiLanguageModel, AiChat} from "@effect/ai"
import {Config, Console, Effect, Layer} from "effect"
import {NodeHttpClient} from "@effect/platform-node"
import { Option } from "effect"
import {employeesToolkit, employeeToolkitLayer} from "./server"

const employeeQuery = (query: string) => Effect.gen(function*() {
  const chat = yield* AiChat.empty

  const maybeResponse = yield* Effect.iterate(Option.none<string>(), {
    while: (state) => Option.isNone(state),
    body: (state) => Effect.gen(function*() {
      const response = yield* chat.generateText({
        prompt: query,
        toolkit: employeesToolkit
      })

      if (response.finishReason === "tool-calls") {
        return state
      }
      else {
        return Option.some(response.text)
      }
    })
  })

  return yield* maybeResponse
})

const novaModel = AmazonBedrockLanguageModel.model("amazon.nova-micro-v1:0")

const amazonBedrock = Layer.provide(
  AmazonBedrockClient.layerConfig({
    accessKeyId: Config.string("AWS_ACCESS_KEY_ID"),
    secretAccessKey: Config.redacted("AWS_SECRET_ACCESS_KEY")
  }),
  NodeHttpClient.layerUndici
)

const main = employeeQuery("list employees that have skills related to AI programming").pipe(
  Effect.provide([novaModel, employeeToolkitLayer])
)

main.pipe(
  Effect.provide(amazonBedrock),
  Effect.runPromise
)
