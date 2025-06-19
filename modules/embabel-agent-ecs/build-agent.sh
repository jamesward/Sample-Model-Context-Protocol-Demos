#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
REPO_PREFIX="embabel-agent-ecs"
COMPONENTS=("server" "client")

# Spinner function
spin() {
    local pid=$1
    local message=$2
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    
    tput civis # Hide cursor
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) % ${#spin} ))
        printf "\r${message} ${spin:$i:1} "
        sleep .1
    done
    tput cnorm # Show cursor
    
    # Check if the process succeeded
    wait $pid
    return $?
}

echo "=================================================="
echo "Build & Push Agent Images to ECR"
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

if ! command -v mvn &> /dev/null && ! [ -f "./mvnw" ]; then
    echo -e "${RED}❌ Maven is not available${NC}"
    echo -e "${YELLOW}💡 Please install Maven or ensure mvnw is present${NC}"
    exit 1
fi

# Use Maven wrapper if available, otherwise use system Maven
if [ -f "./mvnw" ]; then
    MVN="./mvnw"
else
    MVN="mvn"
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

ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${CURRENT_REGION}.amazonaws.com"

echo "📋 Configuration:"
echo "----------------"
echo "Account ID: ${ACCOUNT_ID}"
echo "Region: ${CURRENT_REGION}"
echo "ECR Registry: ${ECR_REGISTRY}"
echo ""

# Check if ECR repositories exist
echo "🔍 Checking ECR repositories..."
echo "------------------------------"

MISSING_REPOS=()
for component in "${COMPONENTS[@]}"; do
    repo_name="${REPO_PREFIX}-${component}"
    echo -n "Repository ${repo_name}: "
    
    if aws ecr describe-repositories --repository-names "${repo_name}" --region "${CURRENT_REGION}" &>/dev/null; then
        echo -e "${GREEN}✅ Exists${NC}"
    else
        echo -e "${RED}❌ Not found${NC}"
        MISSING_REPOS+=("${repo_name}")
    fi
done

if [ ${#MISSING_REPOS[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ Missing ECR repositories: ${MISSING_REPOS[*]}${NC}"
    echo -e "${YELLOW}💡 Run ./setup-ecr.sh first to create repositories and authenticate${NC}"
    exit 1
fi

# Verify Docker authentication
echo ""
echo "🔐 Verifying Docker ECR authentication..."
echo "----------------------------------------"

echo -n "Testing ECR login... "
if docker pull "${ECR_REGISTRY}/hello-world" &>/dev/null 2>&1 || [ $? -eq 1 ]; then
    echo -e "${GREEN}✅ Authenticated${NC}"
else
    echo -e "${YELLOW}⚠️  May need authentication${NC}"
    echo "Attempting to authenticate..."
    
    if aws ecr get-login-password --region "${CURRENT_REGION}" 2>/dev/null | docker login --username AWS --password-stdin "${ECR_REGISTRY}" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Successfully authenticated${NC}"
    else
        echo -e "${RED}❌ Authentication failed${NC}"
        echo -e "${YELLOW}💡 Run ./setup-ecr.sh to authenticate${NC}"
        exit 1
    fi
fi

# Build and push images
echo ""
echo "🏗️  Building and pushing Docker images..."
echo "========================================"

BUILD_FAILED=false

for component in "${COMPONENTS[@]}"; do
    echo ""
    echo "📦 Processing ${component}..."
    echo "----------------------------"
    
    IMAGE_NAME="${ECR_REGISTRY}/${REPO_PREFIX}-${component}"
    
    # Build the image with spinner
    ${MVN} -pl ${component} spring-boot:build-image -Dspring-boot.build-image.imageName="${IMAGE_NAME}" > build-${component}.log 2>&1 &
    BUILD_PID=$!
    
    if spin $BUILD_PID "Building ${component} image"; then
        printf "\r✅ Building ${component} image... ${GREEN}Success${NC}\n"
        
        # Push the image with spinner
        docker push "${IMAGE_NAME}:latest" > push-${component}.log 2>&1 &
        PUSH_PID=$!
        
        if spin $PUSH_PID "Pushing ${component} image"; then
            printf "\r✅ Pushing ${component} image... ${GREEN}Success${NC}\n"
            echo "   Image URI: ${IMAGE_NAME}:latest"
        else
            printf "\r❌ Pushing ${component} image... ${RED}Failed${NC}\n"
            echo -e "${YELLOW}💡 Check push-${component}.log for details${NC}"
            BUILD_FAILED=true
        fi
    else
        printf "\r❌ Building ${component} image... ${RED}Failed${NC}\n"
        echo -e "${YELLOW}💡 Check build-${component}.log for details${NC}"
        BUILD_FAILED=true
    fi
done

# Cleanup log files on success
if [ "$BUILD_FAILED" = false ]; then
    echo ""
    echo "🧹 Cleaning up log files..."
    rm -f build-*.log push-*.log
fi

echo ""
echo "=================================================="

if [ "$BUILD_FAILED" = true ]; then
    echo -e "${RED}❌ Build/push failed for one or more components${NC}"
    echo -e "${YELLOW}💡 Check the log files for details${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All images built and pushed successfully!${NC}"
    echo ""
    echo "📝 Next steps:"
    echo "-------------"
    echo "Deploy the application with Rain:"
    echo -e "${BLUE}rain deploy infra.cfn embabel-agent-ecs${NC}"
    echo ""
    echo "Or if updating an existing deployment:"
    echo -e "${BLUE}rain deploy infra.cfn embabel-agent-ecs --yes${NC}"
fi

echo "=================================================="