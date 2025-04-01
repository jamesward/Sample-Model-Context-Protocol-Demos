#!/bin/bash

set -e

echo "🛑 Stopping MCP Demo..."

# Stop containers
docker-compose down

echo "✅ All containers stopped successfully!" 