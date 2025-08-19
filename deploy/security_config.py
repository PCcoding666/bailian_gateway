#!/usr/bin/env python3
"""
Alibaba Cloud Security Configuration for Bailian Demo
Includes: RAM roles, Security Center, WAF, SSL certificates, and security policies
"""

import json
import yaml
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum

class SecurityLevel(Enum):
    """Security configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"

@dataclass
class RAMRoleConfig:
    """RAM role configuration"""
    role_name: str
    description: str
    assume_role_policy: Dict[str, Any]
    policies: List[str]
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class SecurityGroupRule:
    """Security group rule configuration"""
    direction: str  # ingress/egress
    protocol: str   # tcp/udp/icmp/all
    port_range: str
    source_cidr: str
    description: str
    priority: int = 1

@dataclass 
class SecurityGroupConfig:
    """Security group configuration"""
    name: str
    description: str
    vpc_id: str
    rules: List[SecurityGroupRule]
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class WAFConfig:
    """Web Application Firewall configuration"""
    instance_name: str
    domain: str
    protection_mode: str = "Defense"  # Defense/Block/Warn
    enable_log: bool = True
    enable_cc_protection: bool = True
    enable_region_block: bool = True
    blocked_regions: List[str] = None
    rate_limit: int = 2000  # requests per 5 minutes
    
    def __post_init__(self):
        if self.blocked_regions is None:
            self.blocked_regions = []

@dataclass
class SSLCertificateConfig:
    """SSL certificate configuration"""
    domain: str
    validation_method: str = "DNS"  # DNS/HTTP/EMAIL
    auto_renew: bool = True
    certificate_type: str = "DV"  # DV/OV/EV

class SecurityConfigGenerator:
    """Generate comprehensive security configuration for Bailian Demo"""
    
    def __init__(self, environment: str = "production", security_level: SecurityLevel = SecurityLevel.STANDARD):
        self.environment = environment
        self.security_level = security_level
        self.project_name = "bailian-demo"
        
    def create_ram_roles(self) -> List[RAMRoleConfig]:
        """Create RAM roles for different components"""
        
        # ECS Service Role
        ecs_role = RAMRoleConfig(
            role_name=f"{self.project_name}-ecs-role-{self.environment}",
            description="ECS service role for Bailian Demo backend services",
            assume_role_policy={
                "Version": "1",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": ["ecs.aliyuncs.com"]
                        },
                        "Action": ["sts:AssumeRole"]
                    }
                ]
            },
            policies=[
                "AliyunRDSReadOnlyAccess",
                "AliyunKvstoreReadOnlyAccess", 
                "AliyunOSSReadOnlyAccess",
                "AliyunLogReadOnlyAccess",
                "AliyunCloudMonitorReadOnlyAccess"
            ],
            tags={
                "Environment": self.environment,
                "Project": self.project_name,
                "Component": "backend"
            }
        )
        
        # Function Compute Role
        fc_role = RAMRoleConfig(
            role_name=f"{self.project_name}-fc-role-{self.environment}",
            description="Function Compute role for AI processing",
            assume_role_policy={
                "Version": "1",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": ["fc.aliyuncs.com"]
                        },
                        "Action": ["sts:AssumeRole"]
                    }
                ]
            },
            policies=[
                "AliyunLogFullAccess",
                "AliyunOSSReadOnlyAccess",
                "AliyunRDSReadOnlyAccess"
            ],
            tags={
                "Environment": self.environment,
                "Project": self.project_name,
                "Component": "function-compute"
            }
        )
        
        # Container Registry Role
        cr_role = RAMRoleConfig(
            role_name=f"{self.project_name}-cr-role-{self.environment}",
            description="Container Registry access role",
            assume_role_policy={
                "Version": "1",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": ["ack.aliyuncs.com"]
                        },
                        "Action": ["sts:AssumeRole"]
                    }
                ]
            },
            policies=[
                "AliyunContainerRegistryFullAccess"
            ],
            tags={
                "Environment": self.environment,
                "Project": self.project_name,
                "Component": "container-registry"
            }
        )
        
        # API Gateway Role
        apigateway_role = RAMRoleConfig(
            role_name=f"{self.project_name}-apigateway-role-{self.environment}",
            description="API Gateway service role",
            assume_role_policy={
                "Version": "1",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": ["apigateway.aliyuncs.com"]
                        },
                        "Action": ["sts:AssumeRole"]
                    }
                ]
            },
            policies=[
                "AliyunLogFullAccess",
                "AliyunCloudMonitorFullAccess"
            ],
            tags={
                "Environment": self.environment,
                "Project": self.project_name,
                "Component": "api-gateway"
            }
        )
        
        return [ecs_role, fc_role, cr_role, apigateway_role]
    
    def create_security_groups(self) -> List[SecurityGroupConfig]:
        """Create security groups for different tiers"""
        
        # Web tier security group (ALB)
        web_sg_rules = [
            SecurityGroupRule("ingress", "tcp", "80/80", "0.0.0.0/0", "HTTP access", 1),
            SecurityGroupRule("ingress", "tcp", "443/443", "0.0.0.0/0", "HTTPS access", 1),
            SecurityGroupRule("egress", "all", "-1/-1", "0.0.0.0/0", "All outbound", 1)
        ]
        
        web_sg = SecurityGroupConfig(
            name=f"{self.project_name}-web-sg-{self.environment}",
            description="Security group for web tier (ALB)",
            vpc_id="vpc-placeholder",
            rules=web_sg_rules,
            tags={
                "Environment": self.environment,
                "Project": self.project_name,
                "Tier": "web"
            }
        )
        
        # Application tier security group
        app_sg_rules = [
            SecurityGroupRule("ingress", "tcp", "8000/8000", "10.0.0.0/8", "Backend API", 1),
            SecurityGroupRule("ingress", "tcp", "22/22", "10.0.0.0/8", "SSH access", 2),
            SecurityGroupRule("ingress", "tcp", "9090/9090", "10.0.0.0/8", "Metrics", 3),
            SecurityGroupRule("egress", "all", "-1/-1", "0.0.0.0/0", "All outbound", 1)
        ]
        
        app_sg = SecurityGroupConfig(
            name=f"{self.project_name}-app-sg-{self.environment}",
            description="Security group for application tier",
            vpc_id="vpc-placeholder",
            rules=app_sg_rules,
            tags={
                "Environment": self.environment,
                "Project": self.project_name,
                "Tier": "application"
            }
        )
        
        # Database tier security group
        db_sg_rules = [
            SecurityGroupRule("ingress", "tcp", "3306/3306", "10.0.0.0/8", "MySQL access", 1),
            SecurityGroupRule("ingress", "tcp", "6379/6379", "10.0.0.0/8", "Redis access", 1),
            SecurityGroupRule("egress", "tcp", "3306/3306", "10.0.0.0/8", "MySQL replication", 1)
        ]
        
        db_sg = SecurityGroupConfig(
            name=f"{self.project_name}-db-sg-{self.environment}",
            description="Security group for database tier",
            vpc_id="vpc-placeholder", 
            rules=db_sg_rules,
            tags={
                "Environment": self.environment,
                "Project": self.project_name,
                "Tier": "database"
            }
        )
        
        return [web_sg, app_sg, db_sg]
    
    def create_waf_config(self, domain: str) -> WAFConfig:
        """Create WAF configuration"""
        blocked_regions = []
        
        if self.security_level == SecurityLevel.ENTERPRISE:
            # Block high-risk regions for enterprise
            blocked_regions = ["CN-XJ", "CN-XZ"]  # Example regions
            
        return WAFConfig(
            instance_name=f"{self.project_name}-waf-{self.environment}",
            domain=domain,
            protection_mode="Defense" if self.security_level != SecurityLevel.BASIC else "Warn",
            enable_log=True,
            enable_cc_protection=True,
            enable_region_block=len(blocked_regions) > 0,
            blocked_regions=blocked_regions,
            rate_limit=2000 if self.security_level == SecurityLevel.BASIC else 5000
        )
    
    def create_ssl_config(self, domain: str) -> SSLCertificateConfig:
        """Create SSL certificate configuration"""
        return SSLCertificateConfig(
            domain=domain,
            validation_method="DNS",
            auto_renew=True,
            certificate_type="DV" if self.security_level == SecurityLevel.BASIC else "OV"
        )
    
    def generate_terraform_config(self, domain: str = "bailian-demo.example.com") -> str:
        """Generate Terraform configuration for security resources"""
        
        ram_roles = self.create_ram_roles()
        security_groups = self.create_security_groups()
        waf_config = self.create_waf_config(domain)
        ssl_config = self.create_ssl_config(domain)
        
        terraform_config = f"""
# Alibaba Cloud Security Configuration
# Generated for {self.project_name} - {self.environment} environment

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

variable "domain" {{
  description = "Domain name for SSL and WAF"
  type        = string
  default     = "{domain}"
}}

# Data sources
data "alicloud_vpcs" "default" {{
  name_regex = "default"
}}

# RAM Roles
"""
        
        # Generate RAM roles
        for role in ram_roles:
            role_name_tf = role.role_name.replace("-", "_")
            terraform_config += f"""
resource "alicloud_ram_role" "{role_name_tf}" {{
  name        = "{role.role_name}"
  description = "{role.description}"
  document    = jsonencode({json.dumps(role.assume_role_policy, indent=4)})
  
  tags = {json.dumps(role.tags, indent=4)}
}}
"""
            
            # Attach policies to role
            for i, policy in enumerate(role.policies):
                terraform_config += f"""
resource "alicloud_ram_role_policy_attachment" "{role_name_tf}_policy_{i}" {{
  role_name   = alicloud_ram_role.{role_name_tf}.name
  policy_name = "{policy}"
  policy_type = "System"
}}
"""
        
        # Generate Security Groups
        terraform_config += "\n# Security Groups\n"
        for sg in security_groups:
            sg_name_tf = sg.name.replace("-", "_")
            terraform_config += f"""
resource "alicloud_security_group" "{sg_name_tf}" {{
  name        = "{sg.name}"
  description = "{sg.description}"
  vpc_id      = data.alicloud_vpcs.default.vpcs[0].id
  
  tags = {json.dumps(sg.tags, indent=4)}
}}
"""
            
            # Generate security group rules
            for i, rule in enumerate(sg.rules):
                rule_name = f"{sg_name_tf}_rule_{i}"
                terraform_config += f"""
resource "alicloud_security_group_rule" "{rule_name}" {{
  type              = "{rule.direction}"
  ip_protocol       = "{rule.protocol}"
  port_range        = "{rule.port_range}"
  security_group_id = alicloud_security_group.{sg_name_tf}.id
  cidr_ip          = "{rule.source_cidr}"
  description      = "{rule.description}"
  priority         = {rule.priority}
}}
"""
        
        # Generate WAF configuration
        terraform_config += f"""
# Web Application Firewall
resource "alicloud_waf_instance" "main" {{
  big_screen      = "0"
  exclusive_ip    = "0"
  ext_bandwidth   = "50"
  ext_domain_package = "1"
  package_code    = "version_3"
  prefessional_service = "false"
  subscription_type = "Subscription"
  waf_log         = "true"
  log_storage     = "3"
  log_time        = "180"
  
  tags = {{
    Environment = var.environment
    Project     = var.project_name
  }}
}}

resource "alicloud_waf_domain" "main" {{
  domain_name   = var.domain
  instance_id   = alicloud_waf_instance.main.id
  is_access_product = "On"
  source_ips    = ["1.1.1.1"]  # Replace with ALB IP
  cluster_type  = "PhysicalCluster"
  http2_port    = ["443"]
  http_port     = ["80"]
  https_port    = ["443"]
  http_to_user_ip = "Off"
  https_redirect  = "On"
  load_balancing  = "IpHash"
}}

# WAF Protection Rules
resource "alicloud_waf_protection_module" "cc_protection" {{
  domain     = alicloud_waf_domain.main.domain_name
  instance_id = alicloud_waf_instance.main.id
  defense_type = "cc"
  status     = 1
}}

resource "alicloud_waf_protection_module" "web_attack" {{
  domain     = alicloud_waf_domain.main.domain_name
  instance_id = alicloud_waf_instance.main.id
  defense_type = "waf"
  status     = 1
}}
"""
        
        # Generate SSL Certificate
        terraform_config += f"""
# SSL Certificate
resource "alicloud_ssl_certificates_service_certificate" "main" {{
  certificate_name = "{self.project_name}-ssl-{self.environment}"
  cert             = file("path/to/certificate.crt")
  key              = file("path/to/private.key")
}}
"""
        
        # Generate Security Center configuration
        terraform_config += f"""
# Security Center (Cloud Security Center)
resource "alicloud_threat_detection_baseline_strategy" "main" {{
  baseline_strategy_name = "{self.project_name}-baseline-{self.environment}"
  custom_type           = "custom"
  end_time             = "08:00:00"
  start_time           = "02:00:00"
  target_type          = "groupId"
  cycle_days           = 3
  cycle_start_time     = 3
}}

resource "alicloud_threat_detection_anti_brute_force_rule" "main" {{
  name            = "{self.project_name}-anti-brute-force"
  forbidden_time  = 360
  fail_count      = 5
  span            = 60
  default_rule    = false
  
  uuid_list = ["all"]  # Apply to all assets
}}
"""
        
        # Outputs
        terraform_config += """
# Outputs
output "ram_roles" {
  description = "Created RAM roles"
  value = {
"""
        
        for role in ram_roles:
            role_name_tf = role.role_name.replace("-", "_")
            terraform_config += f'    "{role.role_name}" = alicloud_ram_role.{role_name_tf}.arn\n'
        
        terraform_config += """  }
}

output "security_groups" {
  description = "Created security groups"
  value = {
"""
        
        for sg in security_groups:
            sg_name_tf = sg.name.replace("-", "_")
            terraform_config += f'    "{sg.name}" = alicloud_security_group.{sg_name_tf}.id\n'
        
        terraform_config += """  }
}

output "waf_instance_id" {
  description = "WAF instance ID"
  value       = alicloud_waf_instance.main.id
}

output "ssl_certificate_id" {
  description = "SSL certificate ID"
  value       = alicloud_ssl_certificates_service_certificate.main.id
}
"""
        
        return terraform_config
    
    def generate_security_policies(self) -> Dict[str, Any]:
        """Generate security policies document"""
        return {
            "security_policies": {
                "password_policy": {
                    "minimum_length": 12,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_symbols": True,
                    "password_expiry_days": 90,
                    "password_history": 12
                },
                "session_policy": {
                    "session_timeout": 3600,  # 1 hour
                    "max_concurrent_sessions": 3,
                    "require_mfa": self.security_level != SecurityLevel.BASIC,
                    "session_encryption": True
                },
                "api_security": {
                    "rate_limiting": {
                        "default": "100/minute",
                        "authenticated": "500/minute",
                        "admin": "1000/minute"
                    },
                    "require_https": True,
                    "cors_policy": {
                        "allowed_origins": ["https://*.example.com"],
                        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                        "allow_credentials": True,
                        "max_age": 86400
                    }
                },
                "data_protection": {
                    "encryption_at_rest": True,
                    "encryption_in_transit": True,
                    "key_rotation_days": 365,
                    "backup_encryption": True,
                    "log_encryption": True
                },
                "network_security": {
                    "vpc_isolation": True,
                    "private_subnets": True,
                    "nat_gateway": True,
                    "bastion_host": self.security_level == SecurityLevel.ENTERPRISE,
                    "vpc_flow_logs": True
                },
                "monitoring_and_alerting": {
                    "security_events": True,
                    "failed_login_attempts": True,
                    "privilege_escalation": True,
                    "data_access_anomalies": True,
                    "network_intrusion": True
                }
            },
            "compliance": {
                "standards": ["ISO 27001", "SOC 2", "GDPR"],
                "audit_logging": True,
                "data_retention_days": 2557,  # 7 years
                "privacy_controls": True
            },
            "incident_response": {
                "automated_response": self.security_level == SecurityLevel.ENTERPRISE,
                "notification_channels": ["email", "sms", "slack"],
                "escalation_matrix": {
                    "low": "security-team@company.com",
                    "medium": "security-team@company.com,ops-team@company.com", 
                    "high": "security-team@company.com,ops-team@company.com,management@company.com",
                    "critical": "all-hands@company.com"
                }
            }
        }
    
    def generate_deployment_script(self) -> str:
        """Generate security deployment script"""
        return f"""#!/bin/bash
# Security Configuration Deployment Script
set -e

echo "🔒 Deploying Security Configuration for {self.project_name}..."

# Variables
export ENVIRONMENT="{self.environment}"
export PROJECT_NAME="{self.project_name}"
export SECURITY_LEVEL="{self.security_level.value}"

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
terraform plan -var="environment=$ENVIRONMENT" \\
               -var="project_name=$PROJECT_NAME" \\
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
for i in {{1..10}}; do
    curl -w "%{{http_code}}\\n" -o /dev/null -s https://your-domain.com/api/health
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
"""

def main():
    """Main function to generate security configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Alibaba Cloud security configuration")
    parser.add_argument("--environment", default="production", help="Environment name")
    parser.add_argument("--security-level", choices=["basic", "standard", "enterprise"], 
                       default="standard", help="Security level")
    parser.add_argument("--domain", default="bailian-demo.example.com", help="Domain name")
    
    args = parser.parse_args()
    
    security_level = SecurityLevel(args.security_level)
    generator = SecurityConfigGenerator(args.environment, security_level)
    
    # Generate configurations
    terraform_config = generator.generate_terraform_config(args.domain)
    security_policies = generator.generate_security_policies()
    deployment_script = generator.generate_deployment_script()
    
    # Save configurations
    with open("security_terraform.tf", "w") as f:
        f.write(terraform_config)
    
    with open("security_policies.json", "w") as f:
        json.dump(security_policies, f, indent=2)
    
    with open("deploy_security.sh", "w") as f:
        f.write(deployment_script)
    
    # Make deployment script executable
    import os
    os.chmod("deploy_security.sh", 0o755)
    
    print("✅ Security configuration files generated:")
    print("  - security_terraform.tf (Terraform configuration)")
    print("  - security_policies.json (Security policies)")
    print("  - deploy_security.sh (Deployment script)")
    print(f"  - Security Level: {security_level.value}")
    print(f"  - Environment: {args.environment}")

if __name__ == "__main__":
    main()