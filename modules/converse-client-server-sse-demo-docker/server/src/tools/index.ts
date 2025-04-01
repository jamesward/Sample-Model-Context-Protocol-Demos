import { FastMCP } from "fastmcp";
import { timeTool, TimeParams, timeToolSchema } from './time';
import { s3BucketCount, S3BucketCountParams, s3BucketCountSchema } from './aws/s3BucketCount';

// Export tool types for potential reuse
export type { TimeParams, S3BucketCountParams };
export { timeToolSchema, s3BucketCountSchema };

/**
 * Register all available tools with the FastMCP server.
 * 
 * This function initializes and registers each tool with the server,
 * making them available for use by MCP clients. Tools are registered
 * in the order they are listed here.
 * 
 * Current tools:
 * - timeTool: Get current time in any timezone
 * - s3BucketCount: Count S3 buckets in AWS account
 * 
 * @param server - The FastMCP server instance to register tools with
 */
export const registerTools = (server: FastMCP<Record<string, unknown> | undefined>): void => {
    console.log('\nRegistering tools...');
    
    console.log('- Adding time tool');
    server.addTool(timeTool);
    
    console.log('- Adding S3 bucket count tool');
    server.addTool(s3BucketCount);
    
    console.log('All tools registered\n');
}; 