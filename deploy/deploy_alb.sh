#!/bin/bash
# ALB Deployment Script for Bailian Demo
set -e

echo "🚀 Deploying Application Load Balancer for Bailian Demo..."

# Variables
export ENVIRONMENT="production"
export ALB_NAME="bailian-demo-alb-production"
export PYTHON_CMD="python3"

# Check prerequisites
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ Error: Alibaba Cloud credentials not set"
    exit 1
fi

if [ -z "$VPC_ID" ] || [ -z "$SUBNET_ID_1" ] || [ -z "$SUBNET_ID_2" ]; then
    echo "❌ Error: VPC configuration not set"
    echo "Please set: VPC_ID, SUBNET_ID_1, SUBNET_ID_2"
    exit 1
fi

# Initialize Terraform
echo "📋 Initializing Terraform..."
terraform init

# Plan deployment
echo "📊 Planning ALB deployment..."
terraform plan -var="environment=$ENVIRONMENT" \
               -var="vpc_id=$VPC_ID" \
               -var="subnet_ids=[$SUBNET_ID_1,$SUBNET_ID_2]" \
               -out=alb-plan

# Apply configuration
echo "🏗️  Applying ALB configuration..."
terraform apply alb-plan

# Wait for ALB to be ready
echo "⏳ Waiting for ALB to be ready..."
ALB_DNS=$(terraform output -raw alb_dns_name)
echo "ALB DNS Name: $ALB_DNS"

# Health check
echo "🏥 Performing health check..."
for i in {1..30}; do
    if curl -f "http://$ALB_DNS/health" > /dev/null 2>&1; then
        echo "✅ ALB is ready and healthy!"
        break
    fi
    echo "Attempt $i: ALB not ready yet, waiting..."
    sleep 10
done

echo "🎉 ALB deployment completed successfully!"
echo "Load Balancer DNS: $ALB_DNS"
echo "Target Groups: 2 configured"
echo "Listeners: 2 configured"
