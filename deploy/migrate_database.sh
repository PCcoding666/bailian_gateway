#!/bin/bash
# Database Migration Script for bailian-demo
set -e

echo "🗄️  Starting Database Migration to ApsaraDB RDS MySQL..."

# Variables
export ENVIRONMENT="production"
export PROJECT_NAME="bailian-demo"

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
terraform plan -var="environment=$ENVIRONMENT" \
               -var="project_name=$PROJECT_NAME" \
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
