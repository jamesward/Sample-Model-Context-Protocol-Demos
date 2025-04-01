import { S3Client, ListBucketsCommand } from "@aws-sdk/client-s3";
import { Tool } from 'fastmcp';
import { z } from 'zod';

/**
 * Schema definition for the S3 bucket count tool.
 * 
 * This tool takes no parameters as it simply counts all buckets
 * in the current AWS account.
 */
export const s3BucketCountSchema = z.object({});

// Type inference from the schema
export type S3BucketCountParams = z.infer<typeof s3BucketCountSchema>;

/**
 * S3 Bucket Count Tool
 * 
 * Returns the total number of S3 buckets in the current AWS account.
 * This is a read-only operation that does not modify any resources.
 * 
 * Prerequisites:
 * - AWS credentials must be configured (via environment variables or AWS CLI)
 * - AWS region must be set
 * - IAM permissions: s3:ListBuckets
 * 
 * Example usage:
 * ```typescript
 * const count = await s3BucketCount.execute({})
 * // Returns: "Total S3 buckets: 42"
 * ```
 * 
 * Response format:
 * - Returns a string with the total bucket count
 * - Throws an error if AWS credentials are invalid or missing
 * - Throws an error if IAM permissions are insufficient
 */
export const s3BucketCount: Tool<Record<string, unknown> | undefined, typeof s3BucketCountSchema> = {
    name: 's3BucketCount',
    description: 'Count S3 buckets in AWS account',
    parameters: s3BucketCountSchema,
    execute: async () => {
        console.log('Executing S3 bucket count tool');

        try {
            // Get region from environment variables
            const region = process.env.AWS_REGION;
            if (!region) {
                throw new Error('AWS_REGION environment variable is not set');
            }

            // Create S3 client with explicit region
            const client = new S3Client({
                region: region
            });

            // List all buckets
            const command = new ListBucketsCommand({});
            const response = await client.send(command);

            // Get bucket count
            const count = response.Buckets?.length || 0;

            // Return as a string (FastMCP requirement)
            return `Total S3 buckets: ${count}`;
        } catch (error) {
            if (error instanceof Error) {
                // Enhance error message for common issues
                if (error.message.includes('credentials')) {
                    throw new Error('AWS credentials not found or invalid. Please configure AWS credentials.');
                }
                if (error.message.includes('AccessDenied')) {
                    throw new Error('Access denied. Please check IAM permissions (requires s3:ListBuckets).');
                }
                throw error;
            }
            throw new Error('An unknown error occurred while counting S3 buckets.');
        }
    }
}; 