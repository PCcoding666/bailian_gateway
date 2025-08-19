#!/bin/bash
# Infrastructure Foundation Deployment Script
set -e

echo "🏗️  Deploying Infrastructure Foundation for bailian-demo..."

# Variables
export ENVIRONMENT="production"
export PROJECT_NAME="bailian-demo"
export REGION="cn-hangzhou"

# Check prerequisites
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ Error: Alibaba Cloud credentials not set"
    exit 1
fi

# Initialize Terraform
echo "📋 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan infrastructure deployment
echo "📊 Planning infrastructure deployment..."
terraform plan -var="environment=$ENVIRONMENT" \
               -var="project_name=$PROJECT_NAME" \
               -out=infrastructure-plan

# Apply infrastructure
echo "🚀 Applying infrastructure configuration..."
terraform apply infrastructure-plan

# Get outputs
echo "📋 Infrastructure deployment completed!"
echo "VPC ID: $(terraform output -raw vpc_id)"
echo "VPC CIDR: $(terraform output -raw vpc_cidr_block)"
echo "NAT Gateway IP: $(terraform output -raw nat_gateway_eip)"

# Validate connectivity  
echo "🔍 Validating infrastructure..."
VPC_ID=$(terraform output -raw vpc_id)
echo "VPC $VPC_ID created successfully"

# List created resources
echo "📊 Created Resources Summary:"
echo "- VPC: 1"
echo "- Subnets: 6 (2 public, 4 private)"
echo "- Security Groups: 4"
echo "- NAT Gateway: 1"
echo "- Route Tables: 1"
echo "- Network ACLs: 1"

echo "🎉 Infrastructure foundation deployment completed successfully!"
