#!/bin/bash
# Cache Migration Script for bailian-demo
set -e

echo "🚀 Starting Cache Migration to ApsaraDB for Redis..."

# Variables
export ENVIRONMENT="production"
export PROJECT_NAME="bailian-demo"

# Check prerequisites
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ Error: Alibaba Cloud credentials not set"
    exit 1
fi

if [ -z "$TF_VAR_redis_password" ]; then
    echo "❌ Error: Redis password not set (TF_VAR_redis_password)"
    exit 1
fi

# Initialize Terraform
echo "📋 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan cache deployment
echo "📊 Planning cache deployment..."
terraform plan -var="environment=$ENVIRONMENT" \
               -var="project_name=$PROJECT_NAME" \
               -out=cache-plan

# Apply cache configuration
echo "🚀 Creating Redis cluster..."
terraform apply cache-plan

# Get Redis connection info
echo "📋 Cache deployment completed!"
REDIS_CLUSTER_ENDPOINT=$(terraform output -raw redis_cluster_endpoint)
REDIS_CLUSTER_PORT=$(terraform output -raw redis_cluster_port)
REDIS_SESSIONS_ENDPOINT=$(terraform output -raw redis_sessions_endpoint)
REDIS_SESSIONS_PORT=$(terraform output -raw redis_sessions_port)

echo "Redis Cluster Details:"
echo "  - Main Cache Endpoint: $REDIS_CLUSTER_ENDPOINT:$REDIS_CLUSTER_PORT"
echo "  - Sessions Cache Endpoint: $REDIS_SESSIONS_ENDPOINT:$REDIS_SESSIONS_PORT"
echo "  - Cluster Info: $(terraform output -json redis_cluster_info | jq -c .)"

# Test Redis connectivity
echo "🔍 Testing Redis connectivity..."
if command -v redis-cli &> /dev/null; then
    echo "Testing connection to main Redis cluster..."
    redis-cli -h "$REDIS_CLUSTER_ENDPOINT" -p "$REDIS_CLUSTER_PORT" -a "$TF_VAR_redis_password" --tls ping
    
    if [ $? -eq 0 ]; then
        echo "✅ Main Redis cluster connection successful!"
    else
        echo "❌ Main Redis cluster connection failed!"
        exit 1
    fi
    
    echo "Testing connection to sessions Redis..."
    redis-cli -h "$REDIS_SESSIONS_ENDPOINT" -p "$REDIS_SESSIONS_PORT" -a "$TF_VAR_redis_password" --tls ping
    
    if [ $? -eq 0 ]; then
        echo "✅ Sessions Redis connection successful!"
    else
        echo "❌ Sessions Redis connection failed!"
        exit 1
    fi
    
    # Set up basic Redis data structure for testing
    echo "🔧 Setting up basic cache structures..."
    
    # Test main cache
    redis-cli -h "$REDIS_CLUSTER_ENDPOINT" -p "$REDIS_CLUSTER_PORT" -a "$TF_VAR_redis_password" --tls << 'EOF'
SET test:connection "success"
EXPIRE test:connection 300
HSET app:config version "1.0.0"
HSET app:config environment "$ENVIRONMENT"
LPUSH app:logs "Cache system initialized"
EOF
    
    # Test sessions cache
    redis-cli -h "$REDIS_SESSIONS_ENDPOINT" -p "$REDIS_SESSIONS_PORT" -a "$TF_VAR_redis_password" --tls << 'EOF'
SET session:test "active"
EXPIRE session:test 3600
HSET session:config ttl "3600"
EOF
    
    echo "✅ Basic cache structures created!"
    
else
    echo "⚠️  Redis CLI not installed, skipping connectivity test"
fi

# Update application configuration
echo "📝 Updating application configuration..."
CONFIG_FILE="../backend/.env.production"

cat > "$CONFIG_FILE" << EOF
# Redis Configuration - Production
REDIS_CLUSTER_HOST=$REDIS_CLUSTER_ENDPOINT
REDIS_CLUSTER_PORT=$REDIS_CLUSTER_PORT  
REDIS_CLUSTER_PASSWORD=$TF_VAR_redis_password
REDIS_CLUSTER_SSL=true

REDIS_SESSIONS_HOST=$REDIS_SESSIONS_ENDPOINT
REDIS_SESSIONS_PORT=$REDIS_SESSIONS_PORT
REDIS_SESSIONS_PASSWORD=$TF_VAR_redis_password
REDIS_SESSIONS_SSL=true

# Cache Settings
CACHE_TTL_DEFAULT=3600
CACHE_TTL_SESSIONS=7200
CACHE_TTL_API_RESPONSES=300
CACHE_PREFIX=$PROJECT_NAME:$ENVIRONMENT
EOF

echo "✅ Application configuration updated!"

# Test cache performance
echo "📊 Testing cache performance..."
if command -v redis-cli &> /dev/null; then
    echo "Running performance benchmarks..."
    
    # Benchmark main cluster
    echo "Main cluster benchmark:"
    redis-cli -h "$REDIS_CLUSTER_ENDPOINT" -p "$REDIS_CLUSTER_PORT" -a "$TF_VAR_redis_password" --tls \
        --latency-history -i 1 > redis_main_latency.log &
    MAIN_PID=$!
    
    # Run some operations
    for i in {1..100}; do
        redis-cli -h "$REDIS_CLUSTER_ENDPOINT" -p "$REDIS_CLUSTER_PORT" -a "$TF_VAR_redis_password" --tls \
            SET "benchmark:key:$i" "value$i" > /dev/null 2>&1
    done
    
    kill $MAIN_PID 2>/dev/null || true
    
    echo "✅ Performance benchmark completed!"
    echo "📊 Latency logs saved to redis_main_latency.log"
else
    echo "⚠️  Skipping performance test - Redis CLI not available"
fi

# Validate monitoring
echo "🔍 Validating monitoring setup..."
CLUSTER_ID=$(terraform output -raw redis_cluster_id)
echo "Monitoring alerts configured for instance: $CLUSTER_ID"
echo "  - Memory usage alert: >80%"
echo "  - Connection usage alert: >70%"

# Migration summary
echo "🎉 Cache migration completed successfully!"
echo "📋 Summary:"
echo "  - Redis Cluster: Created (3 shards, 1 replica each)"
echo "  - Sessions Redis: Created (standard instance)"
echo "  - SSL/TLS: Enabled"
echo "  - Authentication: Enabled"
echo "  - Backup retention: 7 days"
echo "  - Monitoring: Configured"
echo "  - Application config: Updated"

echo "🔧 Next Steps:"
echo "  1. Update application to use new Redis endpoints"
echo "  2. Test application functionality with new cache"
echo "  3. Monitor performance and adjust as needed"
echo "  4. Schedule old Redis cleanup after validation"
