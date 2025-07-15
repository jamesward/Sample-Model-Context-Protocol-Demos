import express from "express";
import { Effect, Layer, Console, pipe } from "effect";
import { NodeHttpClient } from "@effect/platform-node";
import { AiLanguageModel } from "@effect/ai";
import { McpClientLive } from "./mcp-client.js";
import { EmployeeToolkit, EmployeeToolHandlers } from "./ai-tools.js";
import { BedrockLanguageModel } from "./bedrock-client.js";

// Define the request/response types
interface InquireRequest {
  question: string;
}

interface InquireResponse {
  answer: string;
}

// Create the main application
const createApp = Effect.gen(function* () {
  const app = express();
  app.use(express.json());

  // Health check endpoint
  app.get("/health", (req, res) => {
    res.json({ status: "healthy" });
  });

  // Main inquiry endpoint
  app.post("/inquire", (req, res) => {
    const { question }: InquireRequest = req.body;

    if (!question) {
      res.status(400).json({ error: "Question is required" });
      return;
    }

    // Create the AI interaction program
    const program = Effect.gen(function* () {
      yield* Console.log(`Processing question: ${question}`);

      // Generate response using AI with tools
      const response = yield* AiLanguageModel.generateText({
        prompt: question,
        toolkit: EmployeeToolkit,
      });

      yield* Console.log(`Generated response: ${response.text}`);
      return response.text;
    });

    // Run the program and send response
    program
      .pipe(
        Effect.provide(BedrockLanguageModel),
        Effect.provide(EmployeeToolHandlers),
        Effect.provide(McpClientLive),
        Effect.runPromise
      )
      .then((answer) => {
        const response: InquireResponse = { answer };
        res.json(response);
      })
      .catch((error) => {
        console.error("Error processing inquiry:", error);
        res.status(500).json({ 
          error: "Internal server error",
          details: error.message 
        });
      });
  });

  return app;
});

// Start the server
const main = Effect.gen(function* () {
  yield* Console.log("Starting Effect AI MCP Client...");
  
  const app = yield* createApp;
  const port = process.env.PORT || 8080;

  yield* Effect.promise(
    () =>
      new Promise<void>((resolve) => {
        app.listen(port, () => {
          console.log(`Server running on port ${port}`);
          resolve();
        });
      })
  );
});

// Run the application
main
  .pipe(
    Effect.provide(NodeHttpClient.layerUndici),
    Effect.runPromise
  )
  .catch((error) => {
    console.error("Failed to start application:", error);
    process.exit(1);
  });
