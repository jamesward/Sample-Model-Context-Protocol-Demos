#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "AWS Configuration Check for Embabel Agent"
echo "=================================================="
echo ""

# 1. Display current AWS profile and region
echo "📋 Current AWS Configuration:"
echo "-----------------------------"

# Get current profile
CURRENT_PROFILE=$(aws configure list-profiles | grep -E "^\*" | sed 's/\* //' || echo "${AWS_PROFILE:-default}")
echo "Profile: ${CURRENT_PROFILE}"

# Get current region
CURRENT_REGION=$(aws configure get region 2>/dev/null || echo "${AWS_REGION:-not set}")
echo "Region: ${CURRENT_REGION}"

# Check if credentials are configured
AWS_ACCESS_KEY=$(aws configure get aws_access_key_id 2>/dev/null)
AWS_SECRET_KEY=$(aws configure get aws_secret_access_key 2>/dev/null)

if [ -n "$AWS_ACCESS_KEY" ] && [ -n "$AWS_SECRET_KEY" ]; then
    echo -e "Credentials: ${GREEN}✅ Configured${NC}"
else
    echo -e "Credentials: ${RED}❌ Not configured${NC}"
    echo -e "${YELLOW}💡 Run 'aws configure' to set up credentials${NC}"
fi

echo ""

# 2. Check required region
echo "🌍 Region Validation:"
echo "--------------------"

# Read required region from application.properties
REQUIRED_REGION=$(grep "spring.ai.bedrock.aws.region" client/src/main/resources/application.properties 2>/dev/null | cut -d'=' -f2 | tr -d ' ')

if [ -z "$REQUIRED_REGION" ]; then
    REQUIRED_REGION="us-east-1"  # Default from the config
fi

echo "Required region: ${REQUIRED_REGION}"

if [ "$CURRENT_REGION" = "$REQUIRED_REGION" ]; then
    echo -e "Region match: ${GREEN}✅ Correct${NC}"
else
    echo -e "Region match: ${RED}❌ Mismatch${NC}"
    echo -e "${YELLOW}💡 Set region to ${REQUIRED_REGION} using: export AWS_REGION=${REQUIRED_REGION}${NC}"
fi

echo ""

# 3. Check Bedrock model access
echo "🤖 Bedrock Model Access Check:"
echo "------------------------------"

# Required models from application.properties
CLAUDE_MODEL="anthropic.claude-sonnet-4-20250514-v1:0"
COHERE_MODEL="cohere.embed-english-v3"

# Check if we can list models (requires proper credentials and region)
if ! aws bedrock list-foundation-models --region "$REQUIRED_REGION" --output json >/dev/null 2>&1; then
    echo -e "${RED}❌ Unable to access Bedrock in region ${REQUIRED_REGION}${NC}"
    echo -e "${YELLOW}💡 Make sure you have:"
    echo "   - Valid AWS credentials configured"
    echo "   - Bedrock access enabled in your AWS account"
    echo "   - Correct permissions to access Bedrock${NC}"
    exit 1
fi

# Check Claude model
echo -n "Claude Sonnet 4 (${CLAUDE_MODEL}): "
if aws bedrock list-foundation-models --region "$REQUIRED_REGION" --output json | jq -e ".modelSummaries[] | select(.modelId == \"${CLAUDE_MODEL}\")" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Available${NC}"
else
    echo -e "${RED}❌ Not found${NC}"
    echo -e "${YELLOW}💡 Request access at: https://us-east-1.console.aws.amazon.com/bedrock/home?region=${REQUIRED_REGION}#/modelaccess${NC}"
fi

# Check Cohere embedding model
echo -n "Cohere Embedding (${COHERE_MODEL}): "
if aws bedrock list-foundation-models --region "$REQUIRED_REGION" --output json | jq -e ".modelSummaries[] | select(.modelId == \"${COHERE_MODEL}\")" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Available${NC}"
else
    echo -e "${RED}❌ Not found${NC}"
    echo -e "${YELLOW}💡 Request access at: https://us-east-1.console.aws.amazon.com/bedrock/home?region=${REQUIRED_REGION}#/modelaccess${NC}"
fi

echo ""

# 4. List all available models
echo "📝 Available Bedrock Models in ${REQUIRED_REGION}:"
echo "----------------------------------------"

MODEL_COUNT=$(aws bedrock list-foundation-models --region "$REQUIRED_REGION" --output json | jq '.modelSummaries | length')
echo "Total models available: ${MODEL_COUNT}"

# Show Anthropic models
echo ""
echo "Anthropic models:"
aws bedrock list-foundation-models --region "$REQUIRED_REGION" --output json | \
    jq -r '.modelSummaries[] | select(.providerName == "Anthropic") | "  - \(.modelId)"'

# Show Cohere models
echo ""
echo "Cohere models:"
aws bedrock list-foundation-models --region "$REQUIRED_REGION" --output json | \
    jq -r '.modelSummaries[] | select(.providerName == "Cohere") | "  - \(.modelId)"'

echo ""

# 5. Check ECR repositories for AWS deployment
echo "🐳 ECR Repository Check (for AWS deployment):"
echo "--------------------------------------------"

# Check if ECR repositories exist
ECR_CLIENT_REPO="embabel-agent-ecs-client"
ECR_SERVER_REPO="embabel-agent-ecs-server"
ECR_REPOS_EXIST=true

echo -n "ECR repository '${ECR_CLIENT_REPO}': "
if aws ecr describe-repositories --repository-names "${ECR_CLIENT_REPO}" --region "$REQUIRED_REGION" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Exists${NC}"
else
    echo -e "${YELLOW}⚠️  Not found${NC}"
    ECR_REPOS_EXIST=false
fi

echo -n "ECR repository '${ECR_SERVER_REPO}': "
if aws ecr describe-repositories --repository-names "${ECR_SERVER_REPO}" --region "$REQUIRED_REGION" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Exists${NC}"
else
    echo -e "${YELLOW}⚠️  Not found${NC}"
    ECR_REPOS_EXIST=false
fi

if [ "$ECR_REPOS_EXIST" = false ]; then
    echo ""
    echo -e "${YELLOW}💡 To create ECR repositories for AWS deployment, run: ./setup-ecr.sh${NC}"
fi

echo ""
echo "=================================================="
echo "✨ Check complete!"
echo ""

# Summary
ALL_GOOD=true
DEPLOYMENT_READY=true

if [ "$CURRENT_REGION" != "$REQUIRED_REGION" ]; then
    ALL_GOOD=false
fi

if ! aws bedrock list-foundation-models --region "$REQUIRED_REGION" --output json | jq -e ".modelSummaries[] | select(.modelId == \"${CLAUDE_MODEL}\")" >/dev/null 2>&1; then
    ALL_GOOD=false
fi

if ! aws bedrock list-foundation-models --region "$REQUIRED_REGION" --output json | jq -e ".modelSummaries[] | select(.modelId == \"${COHERE_MODEL}\")" >/dev/null 2>&1; then
    ALL_GOOD=false
fi

if [ "$ECR_REPOS_EXIST" = false ]; then
    DEPLOYMENT_READY=false
fi

if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✅ All core checks passed! You're ready to run the application locally.${NC}"
    if [ "$DEPLOYMENT_READY" = false ]; then
        echo -e "${YELLOW}⚠️  For AWS deployment: Run ./setup-ecr.sh to create ECR repositories${NC}"
    else
        echo -e "${GREEN}✅ ECR repositories exist - ready for AWS deployment${NC}"
    fi
else
    echo -e "${RED}❌ Some checks failed. Please fix the issues above before running the application.${NC}"
fi

echo "=================================================="