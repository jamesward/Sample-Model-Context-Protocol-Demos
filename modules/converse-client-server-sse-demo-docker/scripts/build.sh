#!/bin/bash

# Exit on any error
set -e

echo "🚀 Building MCP Demo containers..."

# Function to handle errors
handle_error() {
    echo "❌ Error: Build failed!"
    exit 1
}

# Set up error handling
trap 'handle_error' ERR

# Build server
echo "📦 Building server container..."
if docker-compose build mcp-server; then
    echo "✅ Server container built successfully"
else
    echo "❌ Server container build failed"
    exit 1
fi

# Build client
echo "📦 Building client container..."
if docker-compose build mcp-client; then
    echo "✅ Client container built successfully"
else
    echo "❌ Client container build failed"
    exit 1
fi

echo "🎉 All containers built successfully!" 