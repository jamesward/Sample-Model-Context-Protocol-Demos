#!/bin/bash

# Embabel Agent Infrastructure Deployment Script

set -e

# Configuration
BASE_STACK_NAME="embabel-agent-base"
SERVICES_STACK_NAME="embabel-agent-services"
REGION="${AWS_REGION:-us-east-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_rain() {
    if ! command -v rain &> /dev/null; then
        log_error "Rain CLI is not installed. Please install it first."
        exit 1
    fi
}

check_docker_images() {
    log_info "Checking if Docker images exist in ECR..."
    
    # Get account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REPO="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
    
    # Check if repositories exist
    if ! aws ecr describe-repositories --repository-names embabel-agent-ecs-server --region $REGION &> /dev/null; then
        log_warn "Server ECR repository doesn't exist. Creating it..."
        aws ecr create-repository --repository-name embabel-agent-ecs-server --region $REGION
    fi
    
    if ! aws ecr describe-repositories --repository-names embabel-agent-ecs-client --region $REGION &> /dev/null; then
        log_warn "Client ECR repository doesn't exist. Creating it..."
        aws ecr create-repository --repository-name embabel-agent-ecs-client --region $REGION
    fi
    
    log_info "ECR repositories are ready"
}

deploy_base() {
    log_info "Deploying base infrastructure stack..."
    rain deploy "$(dirname "$0")/base.cfn" $BASE_STACK_NAME --region $REGION
    log_info "Base infrastructure deployed successfully!"
}

deploy_services() {
    log_info "Deploying services stack..."
    rain deploy "$(dirname "$0")/services.cfn" $SERVICES_STACK_NAME --region $REGION --params BaseStackName=$BASE_STACK_NAME
    log_info "Services deployed successfully!"
}

update_services() {
    log_info "Updating services (task definitions and ECS services)..."
    rain deploy "$(dirname "$0")/services.cfn" $SERVICES_STACK_NAME --region $REGION --params BaseStackName=$BASE_STACK_NAME
    log_info "Services updated successfully!"
}

cleanup_services() {
    log_info "Removing services stack..."
    if aws cloudformation describe-stacks --stack-name $SERVICES_STACK_NAME --region $REGION &> /dev/null; then
        rain rm $SERVICES_STACK_NAME --region $REGION
        log_info "Services stack removed"
    else
        log_warn "Services stack not found"
    fi
}

cleanup_base() {
    log_info "Removing base infrastructure stack..."
    if aws cloudformation describe-stacks --stack-name $BASE_STACK_NAME --region $REGION &> /dev/null; then
        rain rm $BASE_STACK_NAME --region $REGION
        log_info "Base stack removed"
    else
        log_warn "Base stack not found"
    fi
}

cleanup_all() {
    log_warn "This will remove all infrastructure!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        cleanup_services
        cleanup_base
        log_info "All infrastructure removed"
    else
        log_info "Cleanup cancelled"
    fi
}

get_status() {
    log_info "Checking stack status..."
    
    echo -e "\n${GREEN}Base Infrastructure Stack:${NC}"
    if aws cloudformation describe-stacks --stack-name $BASE_STACK_NAME --region $REGION &> /dev/null; then
        STATUS=$(aws cloudformation describe-stacks --stack-name $BASE_STACK_NAME --region $REGION --query 'Stacks[0].StackStatus' --output text)
        echo "  Status: $STATUS"
        
        if [ "$STATUS" = "CREATE_COMPLETE" ] || [ "$STATUS" = "UPDATE_COMPLETE" ]; then
            LB_DNS=$(aws cloudformation describe-stacks --stack-name $BASE_STACK_NAME --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' --output text)
            echo "  Load Balancer: http://$LB_DNS"
        fi
    else
        echo "  Status: NOT DEPLOYED"
    fi
    
    echo -e "\n${GREEN}Services Stack:${NC}"
    if aws cloudformation describe-stacks --stack-name $SERVICES_STACK_NAME --region $REGION &> /dev/null; then
        STATUS=$(aws cloudformation describe-stacks --stack-name $SERVICES_STACK_NAME --region $REGION --query 'Stacks[0].StackStatus' --output text)
        echo "  Status: $STATUS"
    else
        echo "  Status: NOT DEPLOYED"
    fi
}

build_and_push() {
    log_info "Building and pushing Docker images to ECR..."
    "$(dirname "$0")/build-push.sh"
}

setup_ecr() {
    log_info "Setting up ECR repositories..."
    "$(dirname "$0")/setup-ecr.sh"
}

aws_checks() {
    log_info "Running AWS configuration checks..."
    "$(dirname "$0")/aws-checks.sh"
}

show_help() {
    echo "Embabel Agent Infrastructure Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  aws-checks       Check AWS configuration and Bedrock access"
    echo "  setup-ecr        Setup ECR repositories and Docker authentication"
    echo "  build-push       Build and push Docker images to ECR"
    echo "  all              Deploy all infrastructure (base + services)"
    echo "  base             Deploy only base infrastructure"
    echo "  services         Deploy only services (requires base)"
    echo "  update-services  Update services (redeploy task definitions)"
    echo "  status           Show current deployment status"
    echo "  cleanup-services Remove services stack only"
    echo "  cleanup-base     Remove base infrastructure stack"
    echo "  cleanup-all      Remove all infrastructure"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh aws-checks       # Check AWS setup before deployment"
    echo "  ./deploy.sh setup-ecr        # Setup ECR repositories"
    echo "  ./deploy.sh build-push       # Build and push new images"
    echo "  ./deploy.sh all              # First time deployment"
    echo "  ./deploy.sh update-services  # Update after code changes"
    echo "  ./deploy.sh cleanup-all      # Complete teardown"
}

# Main script logic
check_rain

case "$1" in
    aws-checks)
        aws_checks
        ;;
    setup-ecr)
        setup_ecr
        ;;
    build-push)
        build_and_push
        ;;
    all)
        check_docker_images
        deploy_base
        deploy_services
        get_status
        ;;
    base)
        check_docker_images
        deploy_base
        ;;
    services)
        deploy_services
        ;;
    update-services)
        update_services
        ;;
    status)
        get_status
        ;;
    cleanup-services)
        cleanup_services
        ;;
    cleanup-base)
        cleanup_base
        ;;
    cleanup-all)
        cleanup_all
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac