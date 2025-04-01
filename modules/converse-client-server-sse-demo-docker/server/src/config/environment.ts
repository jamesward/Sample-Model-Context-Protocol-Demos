import { z } from 'zod';

// Environment schema validation
const envSchema = z.object({
    PROJECT_NAME: z.string().default('mcp-server'),
    NODE_ENV: z.string().default('development')
});

// Validate and export environment variables
export const env = envSchema.parse(process.env);

// Version info
export const APP_VERSION = "1.1.0";