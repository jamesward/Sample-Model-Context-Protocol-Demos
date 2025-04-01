export const bedrockConfig = {
    modelId: process.env.BEDROCK_MODEL_ID || 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    region: process.env.AWS_REGION || 'us-west-2',
    systemPrompt: process.env.BEDROCK_SYSTEM_PROMPT || 'You are a helpful assistant.',
    inferenceConfig: {
        maxTokens: 8192,
        temperature: 0.7,
        topP: 0.999,
        stopSequences: []
    },
    anthropicVersion: "bedrock-2023-05-31"
};

export const serverConfig = {
    url: process.env.MCP_SERVER_URL || 'http://localhost:3000'
}; 