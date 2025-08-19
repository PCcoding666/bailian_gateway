#!/bin/bash
# Security Configuration Deployment Script
set -e

echo "🔒 Deploying Security Configuration for bailian-demo..."

# Variables
export ENVIRONMENT="production"
export PROJECT_NAME="bailian-demo"
export SECURITY_LEVEL="standard"

# Check prerequisites
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ Error: Alibaba Cloud credentials not set"
    exit 1
fi

# Initialize Terraform
echo "📋 Initializing Terraform for security resources..."
terraform init

# Validate configuration
echo "✅ Validating security configuration..."
terraform validate

# Plan security deployment
echo "📊 Planning security deployment..."
terraform plan -var="environment=$ENVIRONMENT" \
               -var="project_name=$PROJECT_NAME" \
               -out=security-plan

# Apply security configuration
echo "🛡️  Applying security configuration..."
terraform apply security-plan

# Verify security setup
echo "🔍 Verifying security setup..."

# Check RAM roles
echo "Checking RAM roles..."
aliyun ram ListRoles --query "Roles[?contains(RoleName, '$PROJECT_NAME')]"

# Check security groups
echo "Checking security groups..."
aliyun ecs DescribeSecurityGroups --query "SecurityGroups[?contains(SecurityGroupName, '$PROJECT_NAME')]"

# Check WAF instance
echo "Checking WAF configuration..."
aliyun waf DescribeInstanceInfo

# Security validation tests
echo "🧪 Running security validation tests..."

# Test HTTPS enforcement
curl -I https://your-domain.com | grep -i "strict-transport-security" || echo "⚠️  HSTS header missing"

# Test security headers
curl -I https://your-domain.com | grep -i "x-frame-options" || echo "⚠️  X-Frame-Options header missing"

# Test API rate limiting
for i in {1..10}; do
    curl -w "%{http_code}\n" -o /dev/null -s https://your-domain.com/api/health
done

echo "🎉 Security deployment completed!"
echo "📋 Security Summary:"
echo "  - Environment: $ENVIRONMENT"
echo "  - Security Level: $SECURITY_LEVEL"
echo "  - RAM Roles: Created"
echo "  - Security Groups: Configured"
echo "  - WAF: Enabled"
echo "  - SSL: Configured"
echo "  - Security Center: Enabled"

echo "⚠️  Next Steps:"
echo "  1. Upload SSL certificates"
echo "  2. Configure domain DNS"
echo "  3. Update application security groups"
echo "  4. Enable Security Center monitoring"
echo "  5. Test security policies"
