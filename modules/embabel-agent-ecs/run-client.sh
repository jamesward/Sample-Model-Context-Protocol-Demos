#!/bin/bash

# Export AWS credentials from the configured profile
eval $(aws configure export-credentials --format env)

# Export AWS region
export AWS_REGION=us-east-1

# Print environment variables for debugging
echo "AWS_ACCESS_KEY_ID is set: ${AWS_ACCESS_KEY_ID:+yes}"
echo "AWS_SECRET_ACCESS_KEY is set: ${AWS_SECRET_ACCESS_KEY:+yes}"
echo "AWS_SESSION_TOKEN is set: ${AWS_SESSION_TOKEN:+yes}"
echo "AWS_REGION: $AWS_REGION"

# Run the client with bedrock profile
SPRING_PROFILES_ACTIVE=bedrock ./mvnw -pl client spring-boot:run