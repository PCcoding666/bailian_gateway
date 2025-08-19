
# ApsaraDB for Redis Cluster Configuration
# Distributed caching with high availability

terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.190.0"
    }
  }
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "bailian-demo"
}

variable "redis_password" {
  description = "Redis auth password"
  type        = string
  sensitive   = true
}

# Data sources
data "alicloud_zones" "redis_zones" {
  available_resource_creation = "KVStore"
}

data "alicloud_vpc" "main" {
  name_regex = "bailian-demo-vpc-production"
}

data "alicloud_vswitches" "app_subnets" {
  vpc_id     = data.alicloud_vpc.main.id
  name_regex = "bailian-demo-private-app.*"
}

data "alicloud_security_group" "app" {
  name_regex = "bailian-demo-app-sg"
  vpc_id     = data.alicloud_vpc.main.id
}

# Redis Parameter Group
resource "alicloud_kvstore_parameter_group" "redis_cluster" {
  parameter_group_name = "bailian-demo-redis-params-production"
  engine_version      = "7.0"
  category           = "enhanced"
  
  parameters {
    parameter_name  = "maxmemory-policy"
    parameter_value = "allkeys-lru"
  }
  
  parameters {
    parameter_name  = "timeout"
    parameter_value = "300"
  }
  
  parameters {
    parameter_name  = "tcp-keepalive"
    parameter_value = "60"
  }
  
  parameters {
    parameter_name  = "maxclients"
    parameter_value = "10000"
  }
  
  parameters {
    parameter_name  = "notify-keyspace-events"
    parameter_value = "Ex"
  }
}

# Redis Cluster Instance
resource "alicloud_kvstore_instance" "redis_cluster" {
  instance_name     = "bailian-demo-redis-production"
  instance_class    = "redis.master.large.default"
  engine_version    = "7.0"
  
  # Cluster configuration
  architecture_type = "cluster"
  node_type        = "MASTER_SLAVE"
  shard_count      = 3
  replica_count    = 1
  
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
  
  tags = {
    Name        = "bailian-demo-redis-production"
    Environment = var.environment
    Project     = var.project_name
    Type        = "cluster"
  }
}

# Redis Backup Policy
resource "alicloud_kvstore_backup_policy" "redis_cluster" {
  instance_id   = alicloud_kvstore_instance.redis_cluster.id
  backup_time   = "03:00Z-04:00Z"
  backup_period = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] 
}

# Redis Account for application access
resource "alicloud_kvstore_account" "app_user" {
  instance_id      = alicloud_kvstore_instance.redis_cluster.id
  account_name     = "bailianapp"
  account_password = var.redis_password
  account_type     = "Normal"
  account_privilege = "RoleReadWrite"
  description      = "Application user for bailian-demo"
}

# Connection endpoint
resource "alicloud_kvstore_connection" "redis_cluster" {
  instance_id       = alicloud_kvstore_instance.redis_cluster.id
  connection_string_prefix = "bailian-demo-redis-production"
  port             = "6379"
}

# Additional Redis instance for session storage (separate from main cache)
resource "alicloud_kvstore_instance" "redis_sessions" {
  instance_name     = "bailian-demo-redis-sessions-production"
  instance_class    = "redis.master.small.default"  # 1GB memory
  engine_version    = "7.0"
  
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
  
  tags = {
    Name        = "bailian-demo-redis-sessions-production"
    Environment = var.environment
    Project     = var.project_name
    Type        = "sessions"
  }
}

# Session Redis connection
resource "alicloud_kvstore_connection" "redis_sessions" {
  instance_id       = alicloud_kvstore_instance.redis_sessions.id
  connection_string_prefix = "bailian-demo-redis-sessions-production"
  port             = "6379"
}

# Redis monitoring alerts
resource "alicloud_cms_alarm" "redis_memory_usage" {
  name         = "bailian-demo-redis-memory-usage-production"
  project      = "acs_kvstore"
  metric       = "MemoryUsage"
  dimensions   = {
    instanceId = alicloud_kvstore_instance.redis_cluster.id
  }
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "80"
  triggered_count = 3
  contact_groups = ["default"]
  enabled      = true
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "alicloud_cms_alarm" "redis_connection_usage" {
  name         = "bailian-demo-redis-connections-production"
  project      = "acs_kvstore"
  metric       = "ConnectionUsage"
  dimensions   = {
    instanceId = alicloud_kvstore_instance.redis_cluster.id
  }
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "70"
  triggered_count = 3
  contact_groups = ["default"]
  enabled      = true
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "redis_cluster_id" {
  description = "Redis cluster instance ID"
  value       = alicloud_kvstore_instance.redis_cluster.id
}

output "redis_cluster_endpoint" {
  description = "Redis cluster connection endpoint"
  value       = alicloud_kvstore_connection.redis_cluster.connection_string
}

output "redis_cluster_port" {
  description = "Redis cluster port"
  value       = alicloud_kvstore_connection.redis_cluster.port
}

output "redis_sessions_endpoint" {
  description = "Redis sessions connection endpoint"
  value       = alicloud_kvstore_connection.redis_sessions.connection_string
}

output "redis_sessions_port" {
  description = "Redis sessions port"
  value       = alicloud_kvstore_connection.redis_sessions.port
}

output "redis_cluster_info" {
  description = "Redis cluster configuration"
  value = {
    shards = 3
    replicas_per_shard = 1
    architecture = "cluster"
    version = "7.0"
  }
}
