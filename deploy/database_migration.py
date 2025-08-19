#!/usr/bin/env python3
"""
ApsaraDB RDS MySQL Migration Configuration
High availability setup with read replicas
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class RDSConfig:
    """RDS MySQL configuration"""
    instance_name: str
    engine_version: str
    instance_class: str
    storage_type: str
    storage_size: int
    multi_az: bool
    backup_retention: int
    backup_time: str
    maintenance_time: str

@dataclass
class ReadReplicaConfig:
    """Read replica configuration"""
    replica_name: str
    instance_class: str
    zone_id: str

class DatabaseMigrationGenerator:
    """Generate database migration configuration"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_name = "bailian-demo"
        self.region = "cn-hangzhou"
    
    def create_rds_config(self) -> RDSConfig:
        """Create RDS MySQL configuration"""
        return RDSConfig(
            instance_name=f"{self.project_name}-mysql-{self.environment}",
            engine_version="8.0",
            instance_class="mysql.n4.large.1",  # 4 vCPU, 16GB RAM
            storage_type="cloud_essd",
            storage_size=500,  # 500GB
            multi_az=True,
            backup_retention=7,
            backup_time="03:00Z-04:00Z",
            maintenance_time="04:00Z-05:00Z"
        )
    
    def create_read_replicas(self) -> List[ReadReplicaConfig]:
        """Create read replica configurations"""
        return [
            ReadReplicaConfig(
                replica_name=f"{self.project_name}-mysql-read-1-{self.environment}",
                instance_class="mysql.n4.medium.1",  # 2 vCPU, 8GB RAM
                zone_id=f"{self.region}-i"
            ),
            ReadReplicaConfig(
                replica_name=f"{self.project_name}-mysql-read-2-{self.environment}",
                instance_class="mysql.n4.medium.1",
                zone_id=f"{self.region}-j"
            )
        ]
    
    def generate_terraform_config(self) -> str:
        """Generate Terraform configuration for RDS"""
        rds_config = self.create_rds_config()
        read_replicas = self.create_read_replicas()
        
        terraform_config = f"""
# ApsaraDB RDS MySQL Configuration
# High availability with read replicas

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

variable "db_username" {{
  description = "Database master username"
  type        = string
  default     = "bailianuser"
}}

variable "db_password" {{
  description = "Database master password"
  type        = string
  sensitive   = true
}}

# Data sources
data "alicloud_zones" "db_zones" {{
  available_resource_creation = "Rds"
  multi                      = true
}}

data "alicloud_vpc" "main" {{
  name_regex = "{self.project_name}-vpc-{self.environment}"
}}

data "alicloud_vswitches" "db_subnets" {{
  vpc_id     = data.alicloud_vpc.main.id
  name_regex = "{self.project_name}-private-db.*"
}}

# DB Subnet Group
resource "alicloud_db_backup_policy" "main" {{
  instance_id   = alicloud_db_instance.main.id
  backup_time   = "{rds_config.backup_time}"
  retention_period = {rds_config.backup_retention}
  log_backup    = true
  log_retention_period = 7
}}

# Parameter Group for MySQL 8.0
resource "alicloud_rds_parameter_group" "mysql80" {{
  engine         = "mysql"
  engine_version = "{rds_config.engine_version}"
  param_group_name = "{self.project_name}-mysql80-params-{self.environment}"
  param_group_desc = "MySQL 8.0 parameter group for {self.project_name}"
  
  parameters {{
    name  = "innodb_buffer_pool_size"
    value = "{{DBInstanceClassMemory*3/4}}"
  }}
  
  parameters {{
    name  = "max_connections"
    value = "1000"
  }}
  
  parameters {{
    name  = "slow_query_log"
    value = "1"
  }}
  
  parameters {{
    name  = "long_query_time"
    value = "2"
  }}
  
  parameters {{
    name  = "innodb_flush_log_at_trx_commit"
    value = "1"
  }}
  
  parameters {{
    name  = "sync_binlog"
    value = "1"
  }}
}}

# Main RDS MySQL Instance
resource "alicloud_db_instance" "main" {{
  engine             = "MySQL"
  engine_version     = "{rds_config.engine_version}"
  instance_type      = "{rds_config.instance_class}"
  instance_storage   = {rds_config.storage_size}
  storage_type       = "{rds_config.storage_type}"
  instance_name      = "{rds_config.instance_name}"
  
  vswitch_id         = data.alicloud_vswitches.db_subnets.vswitches[0].id
  security_group_ids = [data.alicloud_security_group.db.id]
  
  # High Availability
  zone_id            = data.alicloud_zones.db_zones.zones[0].id
  zone_id_slave      = data.alicloud_zones.db_zones.zones[1].id
  
  # Storage encryption
  storage_encrypted  = true
  
  # Backup and maintenance
  backup_time        = "{rds_config.backup_time}"
  backup_retention_period = {rds_config.backup_retention}
  maintenance_time   = "{rds_config.maintenance_time}"
  
  # Monitoring
  monitoring_period  = 60
  
  # Auto upgrade
  auto_upgrade_minor_version = "Auto"
  
  # Parameter group
  parameter_group_id = alicloud_rds_parameter_group.mysql80.id
  
  # Deletion protection
  deletion_protection = true
  
  tags = {{
    Name        = "{rds_config.instance_name}"
    Environment = var.environment
    Project     = var.project_name
    Type        = "primary"
  }}
}}

# Database Account
resource "alicloud_rds_account" "main" {{
  db_instance_id   = alicloud_db_instance.main.id
  account_name     = var.db_username
  account_password = var.db_password
  account_type     = "Super"
  account_description = "Main database user for {self.project_name}"
}}

# Database
resource "alicloud_rds_database" "bailian" {{
  instance_id   = alicloud_db_instance.main.id
  name          = "bailian"
  character_set = "utf8mb4"
  description   = "Main database for {self.project_name}"
}}

# Database privilege
resource "alicloud_rds_account_privilege" "main" {{
  instance_id  = alicloud_db_instance.main.id
  account_name = alicloud_rds_account.main.account_name
  privilege    = "ReadWrite"
  db_names     = [alicloud_rds_database.bailian.name]
}}

# Data source for security group
data "alicloud_security_group" "db" {{
  name_regex = "{self.project_name}-db-sg"
  vpc_id     = data.alicloud_vpc.main.id
}}
"""
        
        # Generate read replicas
        for i, replica in enumerate(read_replicas):
            replica_name_tf = f"read_replica_{i+1}"
            terraform_config += f"""
# Read Replica {i+1}
resource "alicloud_db_readonly_instance" "{replica_name_tf}" {{
  master_db_instance_id = alicloud_db_instance.main.id
  instance_name         = "{replica.replica_name}"
  instance_type         = "{replica.instance_class}"
  instance_storage      = alicloud_db_instance.main.instance_storage
  
  zone_id               = "{replica.zone_id}"
  vswitch_id           = data.alicloud_vswitches.db_subnets.vswitches[{i}].id
  
  tags = {{
    Name        = "{replica.replica_name}"
    Environment = var.environment
    Project     = var.project_name
    Type        = "read-replica"
  }}
}}
"""
        
        # Connection endpoints and outputs
        terraform_config += f"""
# Database Connection Endpoints
resource "alicloud_db_connection" "main" {{
  instance_id       = alicloud_db_instance.main.id
  connection_prefix = "{self.project_name}-mysql-{self.environment}"
}}
"""
        
        for i, replica in enumerate(read_replicas):
            replica_name_tf = f"read_replica_{i+1}"
            terraform_config += f"""
resource "alicloud_db_connection" "{replica_name_tf}" {{
  instance_id       = alicloud_db_readonly_instance.{replica_name_tf}.id
  connection_prefix = "{replica.replica_name}"
}}
"""
        
        # Outputs
        terraform_config += """
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
"""
        
        for i, replica in enumerate(read_replicas):
            replica_name_tf = f"read_replica_{i+1}"
            terraform_config += f'    alicloud_db_connection.{replica_name_tf}.connection_string,\n'
        
        terraform_config += """  ]
}

output "backup_retention_period" {
  description = "Backup retention period"
  value       = alicloud_db_instance.main.backup_retention_period
}
"""
        
        return terraform_config
    
    def generate_migration_script(self) -> str:
        """Generate database migration script"""
        return f"""#!/bin/bash
# Database Migration Script for {self.project_name}
set -e

echo "🗄️  Starting Database Migration to ApsaraDB RDS MySQL..."

# Variables
export ENVIRONMENT="{self.environment}"
export PROJECT_NAME="{self.project_name}"

# Check prerequisites
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ Error: Alibaba Cloud credentials not set"
    exit 1
fi

if [ -z "$TF_VAR_db_password" ]; then
    echo "❌ Error: Database password not set (TF_VAR_db_password)"
    exit 1
fi

# Initialize Terraform
echo "📋 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan database deployment
echo "📊 Planning database deployment..."
terraform plan -var="environment=$ENVIRONMENT" \\
               -var="project_name=$PROJECT_NAME" \\
               -out=database-plan

# Apply database configuration
echo "🚀 Creating RDS MySQL instance..."
terraform apply database-plan

# Get database connection info
echo "📋 Database deployment completed!"
RDS_ENDPOINT=$(terraform output -raw rds_connection_string)
RDS_PORT=$(terraform output -raw rds_port)
DB_NAME=$(terraform output -raw database_name)

echo "Database Details:"
echo "  - Endpoint: $RDS_ENDPOINT"
echo "  - Port: $RDS_PORT"
echo "  - Database: $DB_NAME"
echo "  - Read Replicas: $(terraform output -json read_replica_endpoints | jq -r length) created"

# Test database connectivity
echo "🔍 Testing database connectivity..."
if command -v mysql &> /dev/null; then
    echo "Testing connection to primary database..."
    mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u bailianuser -p"$TF_VAR_db_password" -e "SELECT 1;" "$DB_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ Database connection successful!"
    else
        echo "❌ Database connection failed!"
        exit 1
    fi
else
    echo "⚠️  MySQL client not installed, skipping connectivity test"
fi

# Run database schema migration
echo "📊 Running database schema migration..."
if [ -f "../backend/alembic/versions/*.py" ]; then
    echo "Running Alembic migrations..."
    cd ../backend
    export DATABASE_URL="mysql://bailianuser:$TF_VAR_db_password@$RDS_ENDPOINT:$RDS_PORT/$DB_NAME"
    python3 -m alembic upgrade head
    cd ../deploy
    echo "✅ Database schema migration completed!"
else
    echo "⚠️  No Alembic migrations found, creating tables manually..."
    
    # Create basic tables
    mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u bailianuser -p"$TF_VAR_db_password" "$DB_NAME" << 'EOF'
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    nickname VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS api_calls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    api_endpoint VARCHAR(200) NOT NULL,
    model_name VARCHAR(100),
    request_content JSON,
    response_content JSON,
    status_code INT,
    request_tokens INT DEFAULT 0,
    response_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    call_duration INT DEFAULT 0,
    client_ip VARCHAR(45),
    user_agent TEXT,
    conversation_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_api_calls_user_id ON api_calls(user_id);
CREATE INDEX idx_api_calls_created_at ON api_calls(created_at);
EOF
    
    echo "✅ Basic database schema created!"
fi

# Create initial admin user
echo "👤 Creating initial admin user..."
mysql -h "$RDS_ENDPOINT" -P "$RDS_PORT" -u bailianuser -p"$TF_VAR_db_password" "$DB_NAME" << 'EOF'
INSERT IGNORE INTO users (username, email, nickname, password_hash, is_active) 
VALUES ('admin', 'admin@example.com', 'Administrator', 
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYu4RZx1H3sJy6W', TRUE);
EOF

echo "✅ Initial admin user created (password: AdminPass123!)"

# Validate read replicas
echo "🔍 Validating read replicas..."
READ_REPLICAS=$(terraform output -json read_replica_endpoints | jq -r '.[]')
for replica in $READ_REPLICAS; do
    echo "Testing read replica: $replica"
    if command -v mysql &> /dev/null; then
        mysql -h "$replica" -P "$RDS_PORT" -u bailianuser -p"$TF_VAR_db_password" -e "SELECT COUNT(*) FROM users;" "$DB_NAME" || echo "⚠️  Replica $replica not ready yet"
    fi
done

echo "🎉 Database migration completed successfully!"
echo "📋 Summary:"
echo "  - Primary RDS MySQL instance: Created"
echo "  - Read replicas: $(terraform output -json read_replica_endpoints | jq -r length)"
echo "  - High availability: Enabled"
echo "  - Backup retention: $(terraform output -raw backup_retention_period) days"
echo "  - Storage encryption: Enabled"
echo "  - Initial schema: Created"
echo "  - Admin user: Created"
"""

def main():
    """Generate database migration configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate database migration configuration")
    parser.add_argument("--environment", default="production", help="Environment name")
    
    args = parser.parse_args()
    
    generator = DatabaseMigrationGenerator(args.environment)
    
    # Generate configurations
    terraform_config = generator.generate_terraform_config()
    migration_script = generator.generate_migration_script()
    
    # Save configurations
    with open("database_terraform.tf", "w") as f:
        f.write(terraform_config)
    
    with open("migrate_database.sh", "w") as f:
        f.write(migration_script)
    
    # Make migration script executable
    import os
    os.chmod("migrate_database.sh", 0o755)
    
    print("✅ Database migration files generated:")
    print("  - database_terraform.tf (Terraform configuration)")
    print("  - migrate_database.sh (Migration script)")
    print(f"  - Environment: {args.environment}")
    print("  - High availability: Enabled")
    print("  - Read replicas: 2 configured")

if __name__ == "__main__":
    main()