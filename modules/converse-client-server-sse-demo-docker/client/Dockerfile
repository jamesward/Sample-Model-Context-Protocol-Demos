# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies)
RUN npm install

# Copy source code
COPY . .

# Build TypeScript to JavaScript
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy built JavaScript from builder stage
COPY --from=build /app/dist ./dist

# Set environment variables
ENV NODE_ENV=production
ENV MCP_SSE_URL=http://mcp-server:8000/sse

# Create a non-root user and switch to it
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 --ingroup nodejs nodejs

# Change ownership of the app directory to the non-root user
RUN chown -R nodejs:nodejs .

# Switch to non-root user
USER nodejs

# Start the app
CMD ["node", "dist/index.js"] 