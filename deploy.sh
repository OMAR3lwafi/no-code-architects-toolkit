#!/bin/bash

# No-Code Architects Toolkit - Deployment Script
# Usage: ./deploy.sh [environment]
# Environments: dev, staging, prod (default: prod)

set -e

ENVIRONMENT=${1:-prod}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Deploying No-Code Architects Toolkit to $ENVIRONMENT environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Valid environments: dev, staging, prod"
    exit 1
fi

# Check dependencies
print_status "Checking dependencies..."

if ! command -v sam &> /dev/null; then
    print_error "AWS SAM CLI not found. Please install it first."
    print_error "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI not found. Please install it first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

print_success "Dependencies check passed"

# Change to script directory
cd "$SCRIPT_DIR"

# Build the application
print_status "Building SAM application..."
if sam build --cached --parallel; then
    print_success "Build completed successfully"
else
    print_error "Build failed"
    exit 1
fi

# Deploy based on environment
print_status "Deploying to $ENVIRONMENT environment..."

case $ENVIRONMENT in
    dev)
        sam deploy --config-env dev --no-confirm-changeset
        ;;
    staging)
        sam deploy --config-env staging
        ;;
    prod)
        sam deploy --config-env default
        ;;
esac

if [ $? -eq 0 ]; then
    print_success "Deployment completed successfully!"
    
    # Get stack outputs
    print_status "Retrieving deployment information..."
    
    STACK_NAME="no-code-toolkit-$ENVIRONMENT"
    
    # Get Function URL
    FUNCTION_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`FunctionUrl`].OutputValue' \
        --output text 2>/dev/null || echo "Not available")
    
    # Get S3 Bucket
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
        --output text 2>/dev/null || echo "Not available")
    
    # Get Function ARN
    FUNCTION_ARN=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`FunctionArn`].OutputValue' \
        --output text 2>/dev/null || echo "Not available")
    
    echo ""
    echo "🎉 Deployment Summary for $ENVIRONMENT:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📍 Stack Name:    $STACK_NAME"
    echo "🌐 Function URL:  $FUNCTION_URL"
    echo "🪣 S3 Bucket:     $S3_BUCKET"
    echo "🔧 Function ARN:  $FUNCTION_ARN"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Test the deployment
    if [ "$FUNCTION_URL" != "Not available" ]; then
        print_status "Testing deployment..."
        
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$FUNCTION_URL" || echo "000")
        
        if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "404" ]; then
            print_success "Application is responding (HTTP $HTTP_STATUS)"
        else
            print_warning "Application test returned HTTP $HTTP_STATUS"
        fi
    fi
    
    # Show useful commands
    echo ""
    echo "📋 Useful Commands:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 View logs:     sam logs --stack-name $STACK_NAME --tail"
    echo "🧪 Test locally:  sam local start-api"
    echo "🗑️  Delete stack:  sam delete --stack-name $STACK_NAME"
    echo "📈 Monitor:       Open AWS Console → Lambda → Applications → $STACK_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
else
    print_error "Deployment failed"
    exit 1
fi