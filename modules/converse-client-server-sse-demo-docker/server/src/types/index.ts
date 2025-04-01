import { z } from 'zod';

export interface Tool {
    name: string;
    description: string;
    parameters: z.ZodType<any>;
    execute: (params: any) => Promise<string>;
} 