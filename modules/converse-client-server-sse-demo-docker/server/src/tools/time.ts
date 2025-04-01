import { Tool } from 'fastmcp';
import { z } from 'zod';

/**
 * Schema definition for the time tool.
 * 
 * Parameters:
 * - timezone (optional): The timezone to format the time in
 * 
 * Note: The schema and description fields are used by MCP clients (LLMs)
 * to understand how to use this tool.
 */
export const timeToolSchema = z.object({
    timezone: z.string().optional().describe("The timezone to format the time in (e.g. 'America/New_York', 'Australia/Brisbane')")
});

// Type inference from the schema
export type TimeParams = z.infer<typeof timeToolSchema>;

/**
 * Time Tool
 * 
 * Returns the current time formatted according to the specified timezone.
 * If no timezone is provided, UTC is used as the default.
 * 
 * Prerequisites:
 * - None (uses system time)
 * 
 * Example usage:
 * ```typescript
 * // Get time in New York
 * const nyTime = await timeTool.execute({ timezone: 'America/New_York' })
 * // Returns: "Thursday, March 31, 2024 at 12:34:56 PM EDT"
 * 
 * // Get UTC time (default)
 * const utcTime = await timeTool.execute({})
 * // Returns: "Thursday, March 31, 2024 at 4:34:56 PM GMT"
 * ```
 * 
 * Response format:
 * - Returns a string with the full date and time in the requested timezone
 * - Uses US English locale for consistent formatting
 * - Throws an error if the timezone identifier is invalid
 */
export const timeTool: Tool<Record<string, unknown> | undefined, typeof timeToolSchema> = {
    name: 'time',
    description: 'Get the current time in any timezone',
    parameters: timeToolSchema,
    execute: async (params: TimeParams) => {
        console.log('Executing time tool with params:', params);

        // Default to UTC if no timezone provided
        const timezone = params.timezone || 'UTC';

        try {
            // Create a date in the requested timezone
            const date = new Date();
            const timeString = date.toLocaleString('en-US', { 
                timeZone: timezone,
                dateStyle: 'full',
                timeStyle: 'long'
            });

            // Return as a string (FastMCP requirement)
            return timeString;
        } catch (error) {
            if (error instanceof Error && error.message.includes('Invalid time zone')) {
                throw new Error(`Invalid timezone: ${timezone}. Use values like 'UTC', 'America/New_York', etc.`);
            }
            throw error;
        }
    }
}; 