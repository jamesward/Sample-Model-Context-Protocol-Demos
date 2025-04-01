# Use Node.js LTS slim image as base
FROM node:20-slim

# Accept build argument for project name
ARG PROJECT_NAME=mcp-server

# Set working directory
WORKDIR /app

# Set environment variable from build arg
ENV PROJECT_NAME=${PROJECT_NAME}

# Copy dependency files first to leverage Docker cache
COPY package*.json ./
COPY tsconfig.json ./

# Copy source code
COPY src ./src

# Install dependencies and build
RUN npm ci --only=production && \
    # Install dev dependencies for build
    npm ci && \
    # Build TypeScript
    npm run build && \
    # Remove dev dependencies
    npm prune --production

# Document the ports that will be exposed
EXPOSE 8000 8001

# Use non-root user for better security
USER node

# Start the server
CMD ["npm", "start"] 