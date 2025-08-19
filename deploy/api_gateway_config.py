"""
Alibaba Cloud API Gateway Configuration
Handles request routing, rate limiting, and API management
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime

class APIGatewayConfig:
    """Configure Alibaba Cloud API Gateway for the Bailian platform"""
    
    def __init__(self):
        self.gateway_config = {
            'group_name': 'bailian-api-group',
            'group_description': 'Bailian Demo API Gateway Group',
            'region': os.getenv('ALIBABA_CLOUD_REGION', 'cn-hangzhou'),
            'instance_id': os.getenv('API_GATEWAY_INSTANCE_ID', ''),
            'domain': os.getenv('API_GATEWAY_DOMAIN', 'api.bailian.example.com')
        }
        
        self.backend_config = {
            'backend_service': os.getenv('BACKEND_SERVICE_URL', 'http://bailian-backend-service:8000'),
            'health_check_path': '/health/ready',
            'timeout': 30000,  # 30 seconds
            'retry_times': 3
        }
    
    def create_api_definitions(self) -> List[Dict[str, Any]]:
        """Create API definitions for all endpoints"""
        
        apis = [
            # Authentication APIs
            {
                'api_name': 'auth-login',
                'api_description': 'User authentication endpoint',
                'visibility': 'PUBLIC',
                'auth_type': 'ANONYMOUS',
                'request_config': {
                    'request_protocol': 'HTTPS',
                    'request_httpmethod': 'POST',
                    'request_path': '/api/auth/login',
                    'body_format': 'FORM'
                },
                'service_config': {
                    'service_protocol': 'HTTP',
                    'service_httpmethod': 'POST',
                    'service_address': self.backend_config['backend_service'],
                    'service_path': '/api/auth/login',
                    'service_timeout': self.backend_config['timeout']
                },
                'request_parameters': [
                    {
                        'api_parameter_name': 'username',
                        'location': 'BODY',
                        'parameter_type': 'String',
                        'required': 'REQUIRED'
                    },
                    {
                        'api_parameter_name': 'password',
                        'location': 'BODY',
                        'parameter_type': 'String',
                        'required': 'REQUIRED'
                    }
                ]
            },
            
            # Chat Completions API
            {
                'api_name': 'bailian-chat-completions',
                'api_description': 'Qwen model chat completions',
                'visibility': 'PUBLIC',
                'auth_type': 'JWT',
                'request_config': {
                    'request_protocol': 'HTTPS',
                    'request_httpmethod': 'POST',
                    'request_path': '/api/bailian/chat/completions',
                    'body_format': 'STREAM'
                },
                'service_config': {
                    'service_protocol': 'HTTP',
                    'service_httpmethod': 'POST',
                    'service_address': self.backend_config['backend_service'],
                    'service_path': '/api/bailian/chat/completions',
                    'service_timeout': self.backend_config['timeout']
                },
                'request_parameters': [
                    {
                        'api_parameter_name': 'Authorization',
                        'location': 'HEAD',
                        'parameter_type': 'String',
                        'required': 'REQUIRED',
                        'description': 'Bearer JWT token'
                    },
                    {
                        'api_parameter_name': 'model',
                        'location': 'BODY',
                        'parameter_type': 'String',
                        'required': 'REQUIRED'
                    },
                    {
                        'api_parameter_name': 'messages',
                        'location': 'BODY',
                        'parameter_type': 'Array',
                        'required': 'REQUIRED'
                    }
                ],
                'throttling': {
                    'user_throttling': 100,  # requests per minute per user
                    'app_throttling': 1000,  # requests per minute per app
                    'api_throttling': 10000  # requests per minute for this API
                }
            },
            
            # Content Generation API
            {
                'api_name': 'bailian-generation',
                'api_description': 'Wanx model content generation',
                'visibility': 'PUBLIC',
                'auth_type': 'JWT',
                'request_config': {
                    'request_protocol': 'HTTPS',
                    'request_httpmethod': 'POST',
                    'request_path': '/api/bailian/generation',
                    'body_format': 'STREAM'
                },
                'service_config': {
                    'service_protocol': 'HTTP',
                    'service_httpmethod': 'POST',
                    'service_address': self.backend_config['backend_service'],
                    'service_path': '/api/bailian/generation',
                    'service_timeout': 60000  # 60 seconds for generation
                },
                'request_parameters': [
                    {
                        'api_parameter_name': 'Authorization',
                        'location': 'HEAD',
                        'parameter_type': 'String',
                        'required': 'REQUIRED'
                    },
                    {
                        'api_parameter_name': 'model',
                        'location': 'BODY',
                        'parameter_type': 'String',
                        'required': 'REQUIRED'
                    },
                    {
                        'api_parameter_name': 'prompt',
                        'location': 'BODY',
                        'parameter_type': 'String',
                        'required': 'REQUIRED'
                    }
                ],
                'throttling': {
                    'user_throttling': 50,   # requests per minute per user
                    'app_throttling': 500,   # requests per minute per app
                    'api_throttling': 5000   # requests per minute for this API
                }
            },
            
            # Health Check APIs
            {
                'api_name': 'health-check',
                'api_description': 'Service health check',
                'visibility': 'PUBLIC',
                'auth_type': 'ANONYMOUS',
                'request_config': {
                    'request_protocol': 'HTTPS',
                    'request_httpmethod': 'GET',
                    'request_path': '/health',
                    'body_format': 'FORM'
                },
                'service_config': {
                    'service_protocol': 'HTTP',
                    'service_httpmethod': 'GET',
                    'service_address': self.backend_config['backend_service'],
                    'service_path': '/health',
                    'service_timeout': 5000
                },
                'throttling': {
                    'user_throttling': 1000,
                    'app_throttling': 10000,
                    'api_throttling': 100000
                }
            },
            
            # Metrics API
            {
                'api_name': 'metrics',
                'api_description': 'Prometheus metrics endpoint',
                'visibility': 'PRIVATE',
                'auth_type': 'ANONYMOUS',
                'request_config': {
                    'request_protocol': 'HTTPS',
                    'request_httpmethod': 'GET',
                    'request_path': '/metrics',
                    'body_format': 'FORM'
                },
                'service_config': {
                    'service_protocol': 'HTTP',
                    'service_httpmethod': 'GET',
                    'service_address': self.backend_config['backend_service'],
                    'service_path': '/metrics',
                    'service_timeout': 10000
                }
            }
        ]
        
        return apis
    
    def create_throttling_policies(self) -> List[Dict[str, Any]]:
        """Create throttling policies for different user types"""
        
        policies = [
            {
                'throttling_name': 'default-user-policy',
                'throttling_description': 'Default throttling for regular users',
                'unit_time': 60,  # 1 minute
                'api_default': 100,  # default requests per minute
                'user_default': 100,  # default per user
                'app_default': 1000   # default per app
            },
            {
                'throttling_name': 'premium-user-policy',
                'throttling_description': 'Enhanced throttling for premium users',
                'unit_time': 60,
                'api_default': 500,
                'user_default': 500,
                'app_default': 5000
            },
            {
                'throttling_name': 'admin-user-policy',
                'throttling_description': 'High-limit throttling for admin users',
                'unit_time': 60,
                'api_default': 1000,
                'user_default': 1000,
                'app_default': 10000
            }
        ]
        
        return policies
    
    def create_domain_config(self) -> Dict[str, Any]:
        """Create custom domain configuration"""
        
        return {
            'domain_name': self.gateway_config['domain'],
            'certificate_config': {
                'certificate_type': 'CAS',  # Certificate Authority Service
                'certificate_name': f"{self.gateway_config['domain']}-cert",
                'force_https': True
            },
            'cors_config': {
                'allow_origins': [
                    f"https://{os.getenv('CDN_DOMAIN', 'bailian.example.com')}",
                    'https://localhost:3000'  # For development
                ],
                'allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'allow_headers': ['Content-Type', 'Authorization', 'X-Correlation-ID'],
                'expose_headers': ['X-Correlation-ID', 'X-RateLimit-Limit', 'X-RateLimit-Remaining'],
                'allow_credentials': True,
                'max_age': 86400
            }
        }
    
    def create_monitoring_config(self) -> Dict[str, Any]:
        """Create monitoring and logging configuration"""
        
        return {
            'log_config': {
                'enable_access_log': True,
                'enable_error_log': True,
                'log_format': 'JSON',
                'log_retention_days': 30
            },
            'monitoring_config': {
                'enable_monitoring': True,
                'metrics': [
                    'RequestCount',
                    'ErrorCount', 
                    'ResponseTime',
                    'TrafficReceived',
                    'TrafficSent'
                ],
                'alert_rules': [
                    {
                        'rule_name': 'high-error-rate',
                        'metric': 'ErrorRate',
                        'threshold': 5.0,  # 5% error rate
                        'comparison': 'GreaterThanThreshold',
                        'evaluation_periods': 2,
                        'period': 300  # 5 minutes
                    },
                    {
                        'rule_name': 'high-response-time',
                        'metric': 'ResponseTime',
                        'threshold': 5000,  # 5 seconds
                        'comparison': 'GreaterThanThreshold',
                        'evaluation_periods': 3,
                        'period': 300
                    }
                ]
            }
        }
    
    def generate_terraform_config(self) -> str:
        """Generate Terraform configuration for API Gateway"""
        
        terraform_config = f'''
# Alibaba Cloud API Gateway Configuration
terraform {{
  required_providers {{
    alicloud = {{
      source  = "aliyun/alicloud"
      version = "~> 1.0"
    }}
  }}
}}

provider "alicloud" {{
  region = "{self.gateway_config['region']}"
}}

# API Gateway Group
resource "alicloud_api_gateway_group" "bailian_api_group" {{
  name        = "{self.gateway_config['group_name']}"
  description = "{self.gateway_config['group_description']}"
}}

# Custom Domain
resource "alicloud_api_gateway_domain_certificate" "bailian_cert" {{
  domain_name      = "{self.gateway_config['domain']}"
  certificate_body = file("ssl/certificate.crt")
  private_key      = file("ssl/private.key")
  group_id         = alicloud_api_gateway_group.bailian_api_group.id
}}

# Throttling Policies
resource "alicloud_api_gateway_throttling_policy" "default_policy" {{
  throttling_name = "default-user-policy"
  unit_time       = 60
  api_default     = 100
  user_default    = 100
  app_default     = 1000
}}

resource "alicloud_api_gateway_throttling_policy" "premium_policy" {{
  throttling_name = "premium-user-policy"
  unit_time       = 60
  api_default     = 500
  user_default    = 500
  app_default     = 5000
}}

# API Definitions
resource "alicloud_api_gateway_api" "auth_login" {{
  name         = "auth-login"
  group_id     = alicloud_api_gateway_group.bailian_api_group.id
  description  = "User authentication endpoint"
  auth_type    = "ANONYMOUS"
  
  request_config {{
    protocol    = "HTTPS"
    method      = "POST"
    path        = "/api/auth/login"
    mode        = "MAPPING"
  }}
  
  service_type = "HTTP"
  http_service_config {{
    address   = "{self.backend_config['backend_service']}"
    method    = "POST"
    path      = "/api/auth/login"
    timeout   = {self.backend_config['timeout']}
    aone_name = "bailian-backend"
  }}
  
  request_parameters {{
    name         = "username"
    type         = "STRING"
    required     = "REQUIRED"
    in           = "BODY"
    description  = "Username for authentication"
  }}
  
  request_parameters {{
    name         = "password"
    type         = "STRING"
    required     = "REQUIRED"
    in           = "BODY"
    description  = "Password for authentication"
  }}
}}

resource "alicloud_api_gateway_api" "chat_completions" {{
  name         = "bailian-chat-completions"
  group_id     = alicloud_api_gateway_group.bailian_api_group.id
  description  = "Qwen model chat completions"
  auth_type    = "APP"
  
  request_config {{
    protocol    = "HTTPS"
    method      = "POST"
    path        = "/api/bailian/chat/completions"
    mode        = "PASSTHROUGH"
  }}
  
  service_type = "HTTP"
  http_service_config {{
    address   = "{self.backend_config['backend_service']}"
    method    = "POST"
    path      = "/api/bailian/chat/completions"
    timeout   = {self.backend_config['timeout']}
    aone_name = "bailian-backend"
  }}
}}

# Bind throttling policies to APIs
resource "alicloud_api_gateway_throttling_policy_attachment" "chat_throttling" {{
  throttling_policy_id = alicloud_api_gateway_throttling_policy.default_policy.id
  api_id              = alicloud_api_gateway_api.chat_completions.api_id
  group_id            = alicloud_api_gateway_group.bailian_api_group.id
}}

# Output important values
output "api_gateway_group_id" {{
  value = alicloud_api_gateway_group.bailian_api_group.id
}}

output "api_gateway_domain" {{
  value = "{self.gateway_config['domain']}"
}}

output "api_endpoints" {{
  value = {{
    auth_login = "https://{self.gateway_config['domain']}/api/auth/login"
    chat_completions = "https://{self.gateway_config['domain']}/api/bailian/chat/completions"
    generation = "https://{self.gateway_config['domain']}/api/bailian/generation"
    health = "https://{self.gateway_config['domain']}/health"
  }}
}}
'''
        
        return terraform_config
    
    def create_deployment_config(self) -> Dict[str, Any]:
        """Create complete deployment configuration"""
        
        config = {
            'api_gateway': {
                'group_config': self.gateway_config,
                'apis': self.create_api_definitions(),
                'throttling_policies': self.create_throttling_policies(),
                'domain_config': self.create_domain_config(),
                'monitoring_config': self.create_monitoring_config()
            },
            'deployment_info': {
                'created_at': datetime.utcnow().isoformat(),
                'region': self.gateway_config['region'],
                'backend_service': self.backend_config['backend_service']
            }
        }
        
        return config
    
    def save_configurations(self):
        """Save all configuration files"""
        
        # Create deploy directory if it doesn't exist
        os.makedirs('deploy', exist_ok=True)
        
        # Save complete configuration
        config = self.create_deployment_config()
        with open('deploy/api_gateway_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Save Terraform configuration
        terraform_config = self.generate_terraform_config()
        with open('deploy/api_gateway.tf', 'w') as f:
            f.write(terraform_config)
        
        # Create deployment script
        deployment_script = '''#!/bin/bash
# API Gateway Deployment Script

set -e

echo "🚀 Deploying API Gateway to Alibaba Cloud..."

# Check required environment variables
required_vars=("ALIBABA_CLOUD_ACCESS_KEY_ID" "ALIBABA_CLOUD_ACCESS_KEY_SECRET" "ALIBABA_CLOUD_REGION")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ $var is not set"
        exit 1
    fi
done

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -out=api-gateway.tfplan

# Apply deployment (with confirmation)
echo "🚀 Applying deployment..."
terraform apply api-gateway.tfplan

echo "✅ API Gateway deployment completed!"

# Get outputs
echo "📊 Deployment outputs:"
terraform output
'''
        
        with open('deploy/deploy_api_gateway.sh', 'w') as f:
            f.write(deployment_script)
        os.chmod('deploy/deploy_api_gateway.sh', 0o755)
        
        print("✅ API Gateway configuration files created:")
        print("  📄 deploy/api_gateway_config.json - Complete configuration")
        print("  📄 deploy/api_gateway.tf - Terraform infrastructure")
        print("  📄 deploy/deploy_api_gateway.sh - Deployment script")

def main():
    """Main function to generate API Gateway configuration"""
    
    gateway = APIGatewayConfig()
    gateway.save_configurations()
    
    print(f"""
🌐 API Gateway Configuration Summary:
{'='*50}
📍 Region: {gateway.gateway_config['region']}
🏷️  Group: {gateway.gateway_config['group_name']}
🌍 Domain: {gateway.gateway_config['domain']}
🔗 Backend: {gateway.backend_config['backend_service']}

📋 API Endpoints:
  • POST /api/auth/login (Authentication)
  • POST /api/bailian/chat/completions (Chat)
  • POST /api/bailian/generation (Generation)
  • GET /health (Health Check)
  • GET /metrics (Monitoring)

🛡️  Rate Limiting:
  • Default Users: 100 req/min
  • Premium Users: 500 req/min
  • Admin Users: 1000 req/min

🚀 Next Steps:
  1. Set environment variables for Alibaba Cloud credentials
  2. Run: ./deploy/deploy_api_gateway.sh
  3. Configure DNS to point to API Gateway
  4. Test all endpoints
""")

if __name__ == "__main__":
    main()