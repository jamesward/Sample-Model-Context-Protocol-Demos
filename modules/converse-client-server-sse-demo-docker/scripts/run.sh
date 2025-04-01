#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting MCP Demo..."
echo "📦 Getting AWS credentials from your current session..."

# Get the current role being used and verify AWS access
CURRENT_ROLE=$(aws sts get-caller-identity --query 'Arn' --output text)
if [ $? -ne 0 ]; then
    echo "❌ Failed to get AWS credentials. Please check your AWS configuration."
    exit 1
fi
echo "🔑 Using AWS Role: $CURRENT_ROLE"

# Get credentials from current session
echo "🔄 Getting AWS credentials..."
CREDS=$(aws configure export-credentials)
if [ $? -ne 0 ]; then
    echo "❌ Failed to export AWS credentials"
    exit 1
fi

# Extract credentials without evaluating them
AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r '.AccessKeyId')
AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r '.SecretAccessKey')
AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r '.SessionToken // empty')

echo "🌍 Setting AWS Region..."
AWS_REGION=$(aws configure get region)
if [ -z "$AWS_REGION" ]; then
    AWS_REGION="us-west-2"
    echo "⚠️  No AWS region found in config, defaulting to $AWS_REGION"
else
    echo "✅ Using region: $AWS_REGION"
fi

# Base environment variables that are always needed
DOCKER_ENV="AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
AWS_REGION=$AWS_REGION \
MCP_SERVER_URL=http://localhost:8000"

# Only add session token if it exists and is not empty
if [ -n "$AWS_SESSION_TOKEN" ]; then
    DOCKER_ENV="$DOCKER_ENV AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN"
fi

echo "✅ AWS credentials obtained"

echo "🐳 Starting Docker containers..."
# Use the constructed environment variables
eval "$DOCKER_ENV docker-compose up -d"

echo "⏳ Waiting for server to be ready..."
until curl -s http://localhost:8000/health > /dev/null; do
    sleep 1
done
echo "✅ Server is ready!"

# Ask if user wants to connect to client app
read -p "Do you want to connect to the client app? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Connecting to client app..."
    echo "Using AWS credentials from: $CURRENT_ROLE"
    
    docker-compose exec mcp-client npm start
fi

# Show how to reconnect to the client later
echo "To access the client later, run: docker-compose exec mcp-client npm start" 