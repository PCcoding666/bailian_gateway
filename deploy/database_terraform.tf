
# ApsaraDB RDS MySQL Configuration
# High availability with read replicas

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

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "bailianuser"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

# Data sources
data "alicloud_zones" "db_zones" {
  available_resource_creation = "Rds"
  multi                      = true
}

data "alicloud_vpc" "main" {
  name_regex = "bailian-demo-vpc-production"
}

data "alicloud_vswitches" "db_subnets" {
  vpc_id     = data.alicloud_vpc.main.id
  name_regex = "bailian-demo-private-db.*"
}

# DB Subnet Group
resource "alicloud_db_backup_policy" "main" {
  instance_id   = alicloud_db_instance.main.id
  backup_time   = "03:00Z-04:00Z"
  retention_period = 7
  log_backup    = true
  log_retention_period = 7
}

# Parameter Group for MySQL 8.0
resource "alicloud_rds_parameter_group" "mysql80" {
  engine         = "mysql"
  engine_version = "8.0"
  param_group_name = "bailian-demo-mysql80-params-production"
  param_group_desc = "MySQL 8.0 parameter group for bailian-demo"
  
  parameters {
    name  = "innodb_buffer_pool_size"
    value = "{DBInstanceClassMemory*3/4}"
  }
  
  parameters {
    name  = "max_connections"
    value = "1000"
  }
  
  parameters {
    name  = "slow_query_log"
    value = "1"
  }
  
  parameters {
    name  = "long_query_time"
    value = "2"
  }
  
  parameters {
    name  = "innodb_flush_log_at_trx_commit"
    value = "1"
  }
  
  parameters {
    name  = "sync_binlog"
    value = "1"
  }
}

# Main RDS MySQL Instance
resource "alicloud_db_instance" "main" {
  engine             = "MySQL"
  engine_version     = "8.0"
  instance_type      = "mysql.n4.large.1"
  instance_storage   = 500
  storage_type       = "cloud_essd"
  instance_name      = "bailian-demo-mysql-production"
  
  vswitch_id         = data.alicloud_vswitches.db_subnets.vswitches[0].id
  security_group_ids = [data.alicloud_security_group.db.id]
  
  # High Availability
  zone_id            = data.alicloud_zones.db_zones.zones[0].id
  zone_id_slave      = data.alicloud_zones.db_zones.zones[1].id
  
  # Storage encryption
  storage_encrypted  = true
  
  # Backup and maintenance
  backup_time        = "03:00Z-04:00Z"
  backup_retention_period = 7
  maintenance_time   = "04:00Z-05:00Z"
  
  # Monitoring
  monitoring_period  = 60
  
  # Auto upgrade
  auto_upgrade_minor_version = "Auto"
  
  # Parameter group
  parameter_group_id = alicloud_rds_parameter_group.mysql80.id
  
  # Deletion protection
  deletion_protection = true
  
  tags = {
    Name        = "bailian-demo-mysql-production"
    Environment = var.environment
    Project     = var.project_name
    Type        = "primary"
  }
}

# Database Account
resource "alicloud_rds_account" "main" {
  db_instance_id   = alicloud_db_instance.main.id
  account_name     = var.db_username
  account_password = var.db_password
  account_type     = "Super"
  account_description = "Main database user for bailian-demo"
}

# Database
resource "alicloud_rds_database" "bailian" {
  instance_id   = alicloud_db_instance.main.id
  name          = "bailian"
  character_set = "utf8mb4"
  description   = "Main database for bailian-demo"
}

# Database privilege
resource "alicloud_rds_account_privilege" "main" {
  instance_id  = alicloud_db_instance.main.id
  account_name = alicloud_rds_account.main.account_name
  privilege    = "ReadWrite"
  db_names     = [alicloud_rds_database.bailian.name]
}

# Data source for security group
data "alicloud_security_group" "db" {
  name_regex = "bailian-demo-db-sg"
  vpc_id     = data.alicloud_vpc.main.id
}

# Read Replica 1
resource "alicloud_db_readonly_instance" "read_replica_1" {
  master_db_instance_id = alicloud_db_instance.main.id
  instance_name         = "bailian-demo-mysql-read-1-production"
  instance_type         = "mysql.n4.medium.1"
  instance_storage      = alicloud_db_instance.main.instance_storage
  
  zone_id               = "cn-hangzhou-i"
  vswitch_id           = data.alicloud_vswitches.db_subnets.vswitches[0].id
  
  tags = {
    Name        = "bailian-demo-mysql-read-1-production"
    Environment = var.environment
    Project     = var.project_name
    Type        = "read-replica"
  }
}

# Read Replica 2
resource "alicloud_db_readonly_instance" "read_replica_2" {
  master_db_instance_id = alicloud_db_instance.main.id
  instance_name         = "bailian-demo-mysql-read-2-production"
  instance_type         = "mysql.n4.medium.1"
  instance_storage      = alicloud_db_instance.main.instance_storage
  
  zone_id               = "cn-hangzhou-j"
  vswitch_id           = data.alicloud_vswitches.db_subnets.vswitches[1].id
  
  tags = {
    Name        = "bailian-demo-mysql-read-2-production"
    Environment = var.environment
    Project     = var.project_name
    Type        = "read-replica"
  }
}

# Database Connection Endpoints
resource "alicloud_db_connection" "main" {
  instance_id       = alicloud_db_instance.main.id
  connection_prefix = "bailian-demo-mysql-production"
}

resource "alicloud_db_connection" "read_replica_1" {
  instance_id       = alicloud_db_readonly_instance.read_replica_1.id
  connection_prefix = "bailian-demo-mysql-read-1-production"
}

resource "alicloud_db_connection" "read_replica_2" {
  instance_id       = alicloud_db_readonly_instance.read_replica_2.id
  connection_prefix = "bailian-demo-mysql-read-2-production"
}

# Outputs
output "rds_instance_id" {
  description = "RDS instance ID"
  value       = alicloud_db_instance.main.id
}

output "rds_connection_string" {
  description = "RDS connection string"
  value       = alicloud_db_connection.main.connection_string
}

output "rds_port" {
  description = "RDS port"
  value       = alicloud_db_instance.main.port
}

output "database_name" {
  description = "Database name"
  value       = alicloud_rds_database.bailian.name
}

output "read_replica_endpoints" {
  description = "Read replica connection strings"
  value = [
    alicloud_db_connection.read_replica_1.connection_string,
    alicloud_db_connection.read_replica_2.connection_string,
  ]
}

output "backup_retention_period" {
  description = "Backup retention period"
  value       = alicloud_db_instance.main.backup_retention_period
}
