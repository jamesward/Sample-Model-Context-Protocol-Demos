#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
REPO_PREFIX="embabel-agent-ecs"
REPOS=("${REPO_PREFIX}-server" "${REPO_PREFIX}-client")
DELETE_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --delete)
            DELETE_MODE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Setup ECR repositories and Docker authentication for Embabel Agent ECS deployment"
            echo ""
            echo "This script will:"
            echo "  - Create ECR repositories if they don't exist"
            echo "  - Authenticate Docker with ECR"
            echo "  - Can be run multiple times safely"
            echo ""
            echo "Options:"
            echo "  --delete    Remove the ECR repositories"
            echo "  --help      Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "=================================================="
echo "ECR Setup for Embabel Agent ECS"
echo "=================================================="
echo ""

# Check required tools
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed${NC}"
    echo -e "${YELLOW}💡 Please install AWS CLI: https://aws.amazon.com/cli/${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo -e "${YELLOW}💡 Please install Docker: https://www.docker.com/get-started${NC}"
    exit 1
fi

# Get current AWS configuration
CURRENT_REGION=$(aws configure get region 2>/dev/null || echo "${AWS_REGION:-not set}")
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)

if [ -z "$ACCOUNT_ID" ]; then
    echo -e "${RED}❌ Unable to get AWS account ID${NC}"
    echo -e "${YELLOW}💡 Make sure you have valid AWS credentials configured${NC}"
    exit 1
fi

if [ "$CURRENT_REGION" = "not set" ]; then
    echo -e "${RED}❌ AWS region is not set${NC}"
    echo -e "${YELLOW}💡 Set region with: export AWS_REGION=us-east-1${NC}"
    exit 1
fi

echo "📋 AWS Configuration:"
echo "--------------------"
echo "Account ID: ${ACCOUNT_ID}"
echo "Region: ${CURRENT_REGION}"
echo ""

if [ "$DELETE_MODE" = true ]; then
    echo -e "${RED}🗑️  DELETE MODE - Removing ECR repositories${NC}"
    echo ""
    
    # Confirm deletion
    echo -e "${YELLOW}⚠️  This will delete the following repositories:${NC}"
    for repo in "${REPOS[@]}"; do
        echo "   - ${repo}"
    done
    echo ""
    read -p "Are you sure you want to delete these repositories? (yes/no): " -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Deletion cancelled"
        exit 0
    fi
    
    # Delete repositories
    for repo in "${REPOS[@]}"; do
        echo -n "Deleting repository ${repo}... "
        
        if aws ecr delete-repository --repository-name "${repo}" --force --region "${CURRENT_REGION}" 2>/dev/null; then
            echo -e "${GREEN}✅ Deleted${NC}"
        else
            # Check if repository doesn't exist
            if ! aws ecr describe-repositories --repository-names "${repo}" --region "${CURRENT_REGION}" &>/dev/null; then
                echo -e "${YELLOW}⚠️  Repository doesn't exist${NC}"
            else
                echo -e "${RED}❌ Failed to delete${NC}"
            fi
        fi
    done
    
    echo ""
    echo "=================================================="
    echo "✨ Deletion complete!"
    echo "=================================================="
    exit 0
fi

# Normal mode - Create repositories and authenticate

# Step 1: Check and create repositories
echo "📦 Step 1: Checking ECR repositories"
echo "-----------------------------------"

REPOS_CREATED=0
REPOS_EXISTING=0

for repo in "${REPOS[@]}"; do
    echo -n "Repository ${repo}: "
    
    # Check if repository already exists
    if aws ecr describe-repositories --repository-names "${repo}" --region "${CURRENT_REGION}" &>/dev/null; then
        echo -e "${GREEN}✅ Already exists${NC}"
        ((REPOS_EXISTING++))
    else
        # Create the repository
        if aws ecr create-repository --repository-name "${repo}" --region "${CURRENT_REGION}" --output json > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Created${NC}"
            ((REPOS_CREATED++))
        else
            echo -e "${RED}❌ Failed to create${NC}"
            echo -e "${YELLOW}💡 Check your AWS permissions for ECR${NC}"
            exit 1
        fi
    fi
done

echo ""
if [ $REPOS_CREATED -gt 0 ]; then
    echo -e "${GREEN}Created ${REPOS_CREATED} new repository(ies)${NC}"
fi
if [ $REPOS_EXISTING -gt 0 ]; then
    echo -e "${BLUE}Found ${REPOS_EXISTING} existing repository(ies)${NC}"
fi

# Step 2: Authenticate Docker with ECR
echo ""
echo "🔐 Step 2: Authenticating Docker with ECR"
echo "----------------------------------------"

ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${CURRENT_REGION}.amazonaws.com"
echo -n "Logging in to ECR registry... "

if aws ecr get-login-password --region "${CURRENT_REGION}" 2>/dev/null | docker login --username AWS --password-stdin "${ECR_REGISTRY}" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Success${NC}"
else
    echo -e "${RED}❌ Failed${NC}"
    echo -e "${YELLOW}💡 Make sure Docker is running and you have ECR permissions${NC}"
    exit 1
fi

# Step 3: Display repository information
echo ""
echo "📋 Repository Information"
echo "------------------------"

for repo in "${REPOS[@]}"; do
    REPO_URI="${ECR_REGISTRY}/${repo}"
    echo "${repo}: ${REPO_URI}"
done

# Step 4: Show next steps
echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo ""
echo -e "${BLUE}1. Build and push Docker images:${NC}"
echo -e "${BLUE}   ./build-agent.sh${NC}"
echo ""
echo -e "${BLUE}2. Deploy with Rain:${NC}"
echo -e "${BLUE}   rain deploy infra.cfn embabel-agent-ecs${NC}"
echo ""
echo -e "${GREEN}💡 Tip: You can run this script again anytime to refresh your Docker ECR authentication${NC}"