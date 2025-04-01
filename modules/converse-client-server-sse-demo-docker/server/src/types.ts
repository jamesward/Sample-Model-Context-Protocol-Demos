interface TextContent {
    type: "text";
    text: string;
}

interface ImageContent {
    type: "image";
    url: string;
    alt?: string;
}

type ContentResult = TextContent | ImageContent;

export interface Tool {
    name: string;
    description: string;
    inputSchema: {
        type: string;
        properties: Record<string, any>;
        required: string[];
    };
    execute: (input?: any) => Promise<ContentResult>;
} 