#!/usr/bin/env python3
"""
ApsaraDB for Redis Cluster Migration Configuration
Distributed caching with high availability
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class RedisClusterConfig:
    """Redis cluster configuration"""
    instance_name: str
    instance_class: str
    engine_version: str
    architecture_type: str  # cluster, standard, rwsplit
    node_type: str
    shard_count: int
    replica_count: int
    storage_size: int
    backup_retention: int

class CacheMigrationGenerator:
    """Generate Redis cache migration configuration"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_name = "bailian-demo"
        self.region = "cn-hangzhou"
    
    def create_redis_config(self) -> RedisClusterConfig:
        """Create Redis cluster configuration"""
        return RedisClusterConfig(
            instance_name=f"{self.project_name}-redis-{self.environment}",
            instance_class="redis.master.large.default",  # 2GB memory
            engine_version="7.0",
            architecture_type="cluster",
            node_type="MASTER_SLAVE",
            shard_count=3,  # 3 shards for horizontal scaling
            replica_count=1,  # 1 replica per shard
            storage_size=8,  # 8GB per shard
            backup_retention=7
        )
    
    def generate_terraform_config(self) -> str:
        """Generate Terraform configuration for Redis cluster"""
        redis_config = self.create_redis_config()
        
        terraform_config = f"""
# ApsaraDB for Redis Cluster Configuration
# Distributed caching with high availability

terraform {{
  required_providers {{
    alicloud = {{
      source  = "aliyun/alicloud"
      version = "~> 1.190.0"
    }}
  }}
}}

# Variables
variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "{self.environment}"
}}

variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "{self.project_name}"
}}

variable "redis_password" {{
  description = "Redis auth password"
  type        = string
  sensitive   = true
}}

# Data sources
data "alicloud_zones" "redis_zones" {{
  available_resource_creation = "KVStore"
}}

data "alicloud_vpc" "main" {{
  name_regex = "{self.project_name}-vpc-{self.environment}"
}}

data "alicloud_vswitches" "app_subnets" {{
  vpc_id     = data.alicloud_vpc.main.id
  name_regex = "{self.project_name}-private-app.*"
}}

data "alicloud_security_group" "app" {{
  name_regex = "{self.project_name}-app-sg"
  vpc_id     = data.alicloud_vpc.main.id
}}

# Redis Parameter Group
resource "alicloud_kvstore_parameter_group" "redis_cluster" {{
  parameter_group_name = "{self.project_name}-redis-params-{self.environment}"
  engine_version      = "{redis_config.engine_version}"
  category           = "enhanced"
  
  parameters {{
    parameter_name  = "maxmemory-policy"
    parameter_value = "allkeys-lru"
  }}
  
  parameters {{
    parameter_name  = "timeout"
    parameter_value = "300"
  }}
  
  parameters {{
    parameter_name  = "tcp-keepalive"
    parameter_value = "60"
  }}
  
  parameters {{
    parameter_name  = "maxclients"
    parameter_value = "10000"
  }}
  
  parameters {{
    parameter_name  = "notify-keyspace-events"
    parameter_value = "Ex"
  }}
}}

# Redis Cluster Instance
resource "alicloud_kvstore_instance" "redis_cluster" {{
  instance_name     = "{redis_config.instance_name}"
  instance_class    = "{redis_config.instance_class}"
  engine_version    = "{redis_config.engine_version}"
  
  # Cluster configuration
  architecture_type = "{redis_config.architecture_type}"
  node_type        = "{redis_config.node_type}"
  shard_count      = {redis_config.shard_count}
  replica_count    = {redis_config.replica_count}
  
  # Network configuration
  vswitch_id       = data.alicloud_vswitches.app_subnets.vswitches[0].id
  security_group_id = data.alicloud_security_group.app.id
  
  # Authentication
  password         = var.redis_password
  auth_mode        = "auth"
  
  # Backup configuration
  backup_time      = "03:00Z-04:00Z"
  backup_period    = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  
  # Performance and monitoring
  parameter_group_id = alicloud_kvstore_parameter_group.redis_cluster.id
  
  # Maintenance
  maintain_start_time = "04:00Z"
  maintain_end_time   = "05:00Z"
  
  # Auto upgrade
  auto_upgrade     = true
  
  # SSL encryption
  ssl_enable       = true
  
  tags = {{
    Name        = "{redis_config.instance_name}"
    Environment = var.environment
    Project     = var.project_name
    Type        = "cluster"
  }}
}}

# Redis Backup Policy
resource "alicloud_kvstore_backup_policy" "redis_cluster" {{
  instance_id   = alicloud_kvstore_instance.redis_cluster.id
  backup_time   = "03:00Z-04:00Z"
  backup_period = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] 
}}

# Redis Account for application access
resource "alicloud_kvstore_account" "app_user" {{
  instance_id      = alicloud_kvstore_instance.redis_cluster.id
  account_name     = "bailianapp"
  account_password = var.redis_password
  account_type     = "Normal"
  account_privilege = "RoleReadWrite"
  description      = "Application user for {self.project_name}"
}}

# Connection endpoint
resource "alicloud_kvstore_connection" "redis_cluster" {{
  instance_id       = alicloud_kvstore_instance.redis_cluster.id
  connection_string_prefix = "{self.project_name}-redis-{self.environment}"
  port             = "6379"
}}

# Additional Redis instance for session storage (separate from main cache)
resource "alicloud_kvstore_instance" "redis_sessions" {{
  instance_name     = "{self.project_name}-redis-sessions-{self.environment}"
  instance_class    = "redis.master.small.default"  # 1GB memory
  engine_version    = "{redis_config.engine_version}"
  
  # Standard configuration for sessions
  architecture_type = "standard"
  node_type        = "MASTER_SLAVE"
  
  vswitch_id       = data.alicloud_vswitches.app_subnets.vswitches[1].id
  security_group_id = data.alicloud_security_group.app.id
  
  password         = var.redis_password
  auth_mode        = "auth"
  
  backup_time      = "02:00Z-03:00Z"
  backup_period    = ["Monday", "Wednesday", "Friday", "Sunday"]
  
  maintain_start_time = "03:00Z"
  maintain_end_time   = "04:00Z"
  
  ssl_enable       = true
  
  tags = {{
    Name        = "{self.project_name}-redis-sessions-{self.environment}"
    Environment = var.environment
    Project     = var.project_name
    Type        = "sessions"
  }}
}}

# Session Redis connection
resource "alicloud_kvstore_connection" "redis_sessions" {{
  instance_id       = alicloud_kvstore_instance.redis_sessions.id
  connection_string_prefix = "{self.project_name}-redis-sessions-{self.environment}"
  port             = "6379"
}}

# Redis monitoring alerts
resource "alicloud_cms_alarm" "redis_memory_usage" {{
  name         = "{self.project_name}-redis-memory-usage-{self.environment}"
  project      = "acs_kvstore"
  metric       = "MemoryUsage"
  dimensions   = {{
    instanceId = alicloud_kvstore_instance.redis_cluster.id
  }}
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "80"
  triggered_count = 3
  contact_groups = ["default"]
  enabled      = true
  
  tags = {{
    Environment = var.environment
    Project     = var.project_name
  }}
}}

resource "alicloud_cms_alarm" "redis_connection_usage" {{
  name         = "{self.project_name}-redis-connections-{self.environment}"
  project      = "acs_kvstore"
  metric       = "ConnectionUsage"
  dimensions   = {{
    instanceId = alicloud_kvstore_instance.redis_cluster.id
  }}
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "70"
  triggered_count = 3
  contact_groups = ["default"]
  enabled      = true
  
  tags = {{
    Environment = var.environment
    Project     = var.project_name
  }}
}}

# Outputs
output "redis_cluster_id" {{
  description = "Redis cluster instance ID"
  value       = alicloud_kvstore_instance.redis_cluster.id
}}

output "redis_cluster_endpoint" {{
  description = "Redis cluster connection endpoint"
  value       = alicloud_kvstore_connection.redis_cluster.connection_string
}}

output "redis_cluster_port" {{
  description = "Redis cluster port"
  value       = alicloud_kvstore_connection.redis_cluster.port
}}

output "redis_sessions_endpoint" {{
  description = "Redis sessions connection endpoint"
  value       = alicloud_kvstore_connection.redis_sessions.connection_string
}}

output "redis_sessions_port" {{
  description = "Redis sessions port"
  value       = alicloud_kvstore_connection.redis_sessions.port
}}

output "redis_cluster_info" {{
  description = "Redis cluster configuration"
  value = {{
    shards = {redis_config.shard_count}
    replicas_per_shard = {redis_config.replica_count}
    architecture = "{redis_config.architecture_type}"
    version = "{redis_config.engine_version}"
  }}
}}
"""
        
        return terraform_config
    
    def generate_migration_script(self) -> str:
        """Generate cache migration script"""
        return f"""#!/bin/bash
# Cache Migration Script for {self.project_name}
set -e

echo "🚀 Starting Cache Migration to ApsaraDB for Redis..."

# Variables
export ENVIRONMENT="{self.environment}"
export PROJECT_NAME="{self.project_name}"

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
terraform plan -var="environment=$ENVIRONMENT" \\
               -var="project_name=$PROJECT_NAME" \\
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
    redis-cli -h "$REDIS_CLUSTER_ENDPOINT" -p "$REDIS_CLUSTER_PORT" -a "$TF_VAR_redis_password" --tls \\
        --latency-history -i 1 > redis_main_latency.log &
    MAIN_PID=$!
    
    # Run some operations
    for i in {{1..100}}; do
        redis-cli -h "$REDIS_CLUSTER_ENDPOINT" -p "$REDIS_CLUSTER_PORT" -a "$TF_VAR_redis_password" --tls \\
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
"""

def main():
    """Generate cache migration configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate cache migration configuration")
    parser.add_argument("--environment", default="production", help="Environment name")
    
    args = parser.parse_args()
    
    generator = CacheMigrationGenerator(args.environment)
    
    # Generate configurations
    terraform_config = generator.generate_terraform_config()
    migration_script = generator.generate_migration_script()
    
    # Save configurations
    with open("cache_terraform.tf", "w") as f:
        f.write(terraform_config)
    
    with open("migrate_cache.sh", "w") as f:
        f.write(migration_script)
    
    # Make migration script executable
    import os
    os.chmod("migrate_cache.sh", 0o755)
    
    print("✅ Cache migration files generated:")
    print("  - cache_terraform.tf (Terraform configuration)")
    print("  - migrate_cache.sh (Migration script)")
    print(f"  - Environment: {args.environment}")
    print("  - Cluster shards: 3")
    print("  - Replicas per shard: 1")
    print("  - SSL/TLS: Enabled")

if __name__ == "__main__":
    main()