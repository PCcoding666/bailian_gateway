#!/usr/bin/env python3
"""
Application Load Balancer (ALB) Configuration for Bailian Demo
Alibaba Cloud High Availability Setup
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class HealthCheckConfig:
    """Health check configuration for ALB target groups"""
    enabled: bool = True
    protocol: str = "HTTP"
    port: int = 8000
    path: str = "/health/ready"
    interval: int = 30
    timeout: int = 5
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3
    success_codes: str = "200"

@dataclass
class TargetGroupConfig:
    """Target group configuration for ALB"""
    name: str
    protocol: str = "HTTP"
    port: int = 8000
    vpc_id: str = ""
    target_type: str = "ip"
    health_check: HealthCheckConfig = None
    
    def __post_init__(self):
        if self.health_check is None:
            self.health_check = HealthCheckConfig()

@dataclass
class ListenerRule:
    """ALB listener rule configuration"""
    priority: int
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]

@dataclass
class ListenerConfig:
    """ALB listener configuration"""
    port: int
    protocol: str = "HTTP"
    default_actions: List[Dict[str, Any]] = None
    rules: List[ListenerRule] = None
    
    def __post_init__(self):
        if self.default_actions is None:
            self.default_actions = []
        if self.rules is None:
            self.rules = []

@dataclass
class ALBConfig:
    """Main ALB configuration"""
    name: str
    scheme: str = "internet-facing"
    type: str = "application"
    ip_address_type: str = "ipv4"
    vpc_id: str = ""
    subnet_ids: List[str] = None
    security_group_ids: List[str] = None
    target_groups: List[TargetGroupConfig] = None
    listeners: List[ListenerConfig] = None
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.subnet_ids is None:
            self.subnet_ids = []
        if self.security_group_ids is None:
            self.security_group_ids = []
        if self.target_groups is None:
            self.target_groups = []
        if self.listeners is None:
            self.listeners = []
        if self.tags is None:
            self.tags = {}

class ALBConfigGenerator:
    """Generate ALB configuration for Bailian Demo"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.config = self._create_base_config()
    
    def _create_base_config(self) -> ALBConfig:
        """Create base ALB configuration"""
        return ALBConfig(
            name=f"bailian-demo-alb-{self.environment}",
            scheme="internet-facing",
            type="application",
            ip_address_type="ipv4",
            tags={
                "Environment": self.environment,
                "Project": "bailian-demo",
                "ManagedBy": "terraform",
                "Component": "load-balancer"
            }
        )
    
    def add_backend_target_group(self, vpc_id: str) -> 'ALBConfigGenerator':
        """Add backend API target group"""
        backend_tg = TargetGroupConfig(
            name=f"bailian-backend-tg-{self.environment}",
            protocol="HTTP",
            port=8000,
            vpc_id=vpc_id,
            target_type="ip",
            health_check=HealthCheckConfig(
                enabled=True,
                protocol="HTTP",
                port=8000,
                path="/health/ready",
                interval=30,
                timeout=5,
                healthy_threshold=2,
                unhealthy_threshold=3,
                success_codes="200"
            )
        )
        self.config.target_groups.append(backend_tg)
        return self
    
    def add_metrics_target_group(self, vpc_id: str) -> 'ALBConfigGenerator':
        """Add metrics endpoint target group"""
        metrics_tg = TargetGroupConfig(
            name=f"bailian-metrics-tg-{self.environment}",
            protocol="HTTP",
            port=8000,
            vpc_id=vpc_id,
            target_type="ip",
            health_check=HealthCheckConfig(
                enabled=True,
                protocol="HTTP",
                port=8000,
                path="/metrics",
                interval=60,
                timeout=10,
                healthy_threshold=2,
                unhealthy_threshold=2,
                success_codes="200"
            )
        )
        self.config.target_groups.append(metrics_tg)
        return self
    
    def add_http_listener(self) -> 'ALBConfigGenerator':
        """Add HTTP listener with routing rules"""
        # Define routing rules
        api_rule = ListenerRule(
            priority=100,
            conditions=[
                {
                    "field": "path-pattern",
                    "values": ["/api/*"]
                }
            ],
            actions=[
                {
                    "type": "forward",
                    "target_group_arn": f"bailian-backend-tg-{self.environment}"
                }
            ]
        )
        
        health_rule = ListenerRule(
            priority=200,
            conditions=[
                {
                    "field": "path-pattern", 
                    "values": ["/health*"]
                }
            ],
            actions=[
                {
                    "type": "forward",
                    "target_group_arn": f"bailian-backend-tg-{self.environment}"
                }
            ]
        )
        
        metrics_rule = ListenerRule(
            priority=300,
            conditions=[
                {
                    "field": "path-pattern",
                    "values": ["/metrics"]
                }
            ],
            actions=[
                {
                    "type": "forward",
                    "target_group_arn": f"bailian-metrics-tg-{self.environment}"
                }
            ]
        )
        
        # HTTP Listener
        http_listener = ListenerConfig(
            port=80,
            protocol="HTTP",
            default_actions=[
                {
                    "type": "redirect",
                    "redirect": {
                        "protocol": "HTTPS",
                        "port": "443",
                        "status_code": "HTTP_301"
                    }
                }
            ],
            rules=[api_rule, health_rule, metrics_rule]
        )
        
        self.config.listeners.append(http_listener)
        return self
    
    def add_https_listener(self, certificate_arn: str = None) -> 'ALBConfigGenerator':
        """Add HTTPS listener with SSL termination"""
        # Default actions for HTTPS listener
        default_actions = [
            {
                "type": "forward",
                "target_group_arn": f"bailian-backend-tg-{self.environment}"
            }
        ]
        
        https_listener = ListenerConfig(
            port=443,
            protocol="HTTPS",
            default_actions=default_actions
        )
        
        # Add certificate if provided
        if certificate_arn:
            https_listener.certificate_arn = certificate_arn
        
        self.config.listeners.append(https_listener)
        return self
    
    def set_vpc_config(self, vpc_id: str, subnet_ids: List[str], security_group_ids: List[str]) -> 'ALBConfigGenerator':
        """Set VPC configuration"""
        self.config.vpc_id = vpc_id
        self.config.subnet_ids = subnet_ids
        self.config.security_group_ids = security_group_ids
        return self
    
    def generate_terraform_config(self) -> str:
        """Generate Terraform configuration for ALB"""
        terraform_config = f"""
# Application Load Balancer Configuration
resource "alicloud_alb_load_balancer" "bailian_alb" {{
  load_balancer_name = "{self.config.name}"
  load_balancer_type = "{self.config.type}"
  scheme             = "{self.config.scheme}"
  vpc_id            = "{self.config.vpc_id}"
  
  zone_mappings {{
    zone_id    = data.alicloud_zones.default.zones[0].id
    subnet_id  = "{self.config.subnet_ids[0] if self.config.subnet_ids else 'SUBNET_ID_1'}"
  }}
  
  zone_mappings {{
    zone_id    = data.alicloud_zones.default.zones[1].id
    subnet_id  = "{self.config.subnet_ids[1] if len(self.config.subnet_ids) > 1 else 'SUBNET_ID_2'}"
  }}
  
  security_group_ids = {json.dumps(self.config.security_group_ids or ["SECURITY_GROUP_ID"])}
  
  tags = {json.dumps(self.config.tags, indent=4)}
}}

# Target Groups
"""
        
        # Generate target group configurations
        for tg in self.config.target_groups:
            terraform_config += f"""
resource "alicloud_alb_server_group" "{tg.name.replace('-', '_')}" {{
  server_group_name = "{tg.name}"
  vpc_id           = "{tg.vpc_id or self.config.vpc_id}"
  protocol         = "{tg.protocol}"
  
  health_check_config {{
    health_check_enabled         = {str(tg.health_check.enabled).lower()}
    health_check_protocol        = "{tg.health_check.protocol}"
    health_check_port           = {tg.health_check.port}
    health_check_path           = "{tg.health_check.path}"
    health_check_interval       = {tg.health_check.interval}
    health_check_timeout        = {tg.health_check.timeout}
    unhealthy_threshold         = {tg.health_check.unhealthy_threshold}
    healthy_threshold           = {tg.health_check.healthy_threshold}
    health_check_http_codes     = ["{tg.health_check.success_codes}"]
  }}
  
  tags = {json.dumps(self.config.tags)}
}}
"""
        
        # Generate listener configurations
        for listener in self.config.listeners:
            listener_name = f"{self.config.name.replace('-', '_')}_listener_{listener.port}"
            terraform_config += f"""
resource "alicloud_alb_listener" "{listener_name}" {{
  load_balancer_id = alicloud_alb_load_balancer.bailian_alb.id
  listener_protocol = "{listener.protocol}"
  listener_port    = {listener.port}
  
  default_actions {{
"""
            # Add default actions
            for action in listener.default_actions:
                if action["type"] == "forward":
                    terraform_config += f"""    type = "ForwardGroup"
    forward_group_config {{
      server_group_tuples {{
        server_group_id = alicloud_alb_server_group.{action["target_group_arn"].replace('-', '_')}.id
      }}
    }}
"""
                elif action["type"] == "redirect":
                    redirect = action["redirect"]
                    terraform_config += f"""    type = "Redirect"
    redirect_config {{
      protocol    = "{redirect['protocol']}"
      port        = "{redirect['port']}"
      http_code   = "{redirect['status_code']}"
    }}
"""
            
            terraform_config += "  }\n}\n"
        
        # Add data sources
        terraform_config += """
# Data sources
data "alicloud_zones" "default" {
  available_resource_creation = "VSwitch"
}

# Outputs
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = alicloud_alb_load_balancer.bailian_alb.dns_name
}

output "alb_id" {
  description = "ID of the load balancer"
  value       = alicloud_alb_load_balancer.bailian_alb.id
}

output "target_group_arns" {
  description = "ARNs of the target groups"
  value = {
"""
        
        for tg in self.config.target_groups:
            terraform_config += f'    "{tg.name}" = alicloud_alb_server_group.{tg.name.replace("-", "_")}.id\n'
        
        terraform_config += "  }\n}\n"
        
        return terraform_config
    
    def generate_deployment_script(self) -> str:
        """Generate deployment script for ALB setup"""
        return f"""#!/bin/bash
# ALB Deployment Script for Bailian Demo
set -e

echo "🚀 Deploying Application Load Balancer for Bailian Demo..."

# Variables
export ENVIRONMENT="{self.environment}"
export ALB_NAME="{self.config.name}"

# Check prerequisites
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ Error: Alibaba Cloud credentials not set"
    exit 1
fi

if [ -z "$VPC_ID" ] || [ -z "$SUBNET_ID_1" ] || [ -z "$SUBNET_ID_2" ]; then
    echo "❌ Error: VPC configuration not set"
    echo "Please set: VPC_ID, SUBNET_ID_1, SUBNET_ID_2"
    exit 1
fi

# Initialize Terraform
echo "📋 Initializing Terraform..."
terraform init

# Plan deployment
echo "📊 Planning ALB deployment..."
terraform plan -var="environment=$ENVIRONMENT" \\
               -var="vpc_id=$VPC_ID" \\
               -var="subnet_ids=[$SUBNET_ID_1,$SUBNET_ID_2]" \\
               -out=alb-plan

# Apply configuration
echo "🏗️  Applying ALB configuration..."
terraform apply alb-plan

# Wait for ALB to be ready
echo "⏳ Waiting for ALB to be ready..."
ALB_DNS=$(terraform output -raw alb_dns_name)
echo "ALB DNS Name: $ALB_DNS"

# Health check
echo "🏥 Performing health check..."
for i in {{1..30}}; do
    if curl -f "http://$ALB_DNS/health" > /dev/null 2>&1; then
        echo "✅ ALB is ready and healthy!"
        break
    fi
    echo "Attempt $i: ALB not ready yet, waiting..."
    sleep 10
done

echo "🎉 ALB deployment completed successfully!"
echo "Load Balancer DNS: $ALB_DNS"
echo "Target Groups: {len(self.config.target_groups)} configured"
echo "Listeners: {len(self.config.listeners)} configured"
"""

def main():
    """Main function to generate ALB configuration"""
    # Create ALB configuration for production
    alb_generator = ALBConfigGenerator("production")
    
    # Configure ALB with target groups and listeners
    alb_generator.add_backend_target_group("vpc-xxxxxxxxx")
    alb_generator.add_metrics_target_group("vpc-xxxxxxxxx")
    alb_generator.add_http_listener()
    alb_generator.add_https_listener()
    alb_generator.set_vpc_config(
        vpc_id="vpc-xxxxxxxxx",
        subnet_ids=["vsw-xxxxxxxxx", "vsw-yyyyyyyyy"],
        security_group_ids=["sg-xxxxxxxxx"]
    )
    
    # Generate configurations
    terraform_config = alb_generator.generate_terraform_config()
    deployment_script = alb_generator.generate_deployment_script()
    
    # Save configurations
    with open("alb_terraform.tf", "w") as f:
        f.write(terraform_config)
    
    with open("deploy_alb.sh", "w") as f:
        f.write(deployment_script)
    
    # Generate JSON config for API reference
    config_dict = asdict(alb_generator.config)
    with open("alb_config.json", "w") as f:
        json.dump(config_dict, f, indent=2)
    
    print("✅ ALB configuration files generated:")
    print("  - alb_terraform.tf (Terraform configuration)")
    print("  - deploy_alb.sh (Deployment script)")
    print("  - alb_config.json (Configuration reference)")

if __name__ == "__main__":
    main()