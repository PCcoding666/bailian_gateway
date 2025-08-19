#!/usr/bin/env python3
"""
Alibaba Cloud Infrastructure Foundation
Complete IaC templates for VPC, security groups, and networking
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class SubnetConfig:
    """Subnet configuration"""
    name: str
    cidr_block: str
    zone_id: str
    type: str  # public, private
    description: str

@dataclass
class VPCConfig:
    """VPC configuration"""
    name: str
    cidr_block: str
    description: str
    subnets: List[SubnetConfig]
    enable_dns: bool = True
    enable_dns_hostnames: bool = True

@dataclass
class SecurityGroupRule:
    """Security group rule"""
    type: str  # ingress/egress
    protocol: str  # tcp/udp/icmp/all
    port_range: str
    source_cidr: str
    description: str
    priority: int = 1

@dataclass
class SecurityGroupConfig:
    """Security group configuration"""
    name: str
    description: str
    rules: List[SecurityGroupRule]

class InfrastructureFoundationGenerator:
    """Generate complete infrastructure foundation"""
    
    def __init__(self, environment: str = "production", region: str = "cn-hangzhou"):
        self.environment = environment
        self.region = region
        self.project_name = "bailian-demo"
        
    def create_vpc_config(self) -> VPCConfig:
        """Create VPC configuration with multi-AZ subnets"""
        subnets = [
            # Public subnets for ALB
            SubnetConfig(
                name=f"{self.project_name}-public-subnet-a",
                cidr_block="10.0.1.0/24",
                zone_id=f"{self.region}-h",
                type="public",
                description="Public subnet for load balancers in AZ-A"
            ),
            SubnetConfig(
                name=f"{self.project_name}-public-subnet-b", 
                cidr_block="10.0.2.0/24",
                zone_id=f"{self.region}-i",
                type="public",
                description="Public subnet for load balancers in AZ-B"
            ),
            
            # Private subnets for applications
            SubnetConfig(
                name=f"{self.project_name}-private-app-subnet-a",
                cidr_block="10.0.11.0/24",
                zone_id=f"{self.region}-h",
                type="private",
                description="Private subnet for application servers in AZ-A"
            ),
            SubnetConfig(
                name=f"{self.project_name}-private-app-subnet-b",
                cidr_block="10.0.12.0/24", 
                zone_id=f"{self.region}-i",
                type="private",
                description="Private subnet for application servers in AZ-B"
            ),
            
            # Private subnets for databases
            SubnetConfig(
                name=f"{self.project_name}-private-db-subnet-a",
                cidr_block="10.0.21.0/24",
                zone_id=f"{self.region}-h",
                type="private",
                description="Private subnet for databases in AZ-A"
            ),
            SubnetConfig(
                name=f"{self.project_name}-private-db-subnet-b",
                cidr_block="10.0.22.0/24",
                zone_id=f"{self.region}-i", 
                type="private",
                description="Private subnet for databases in AZ-B"
            )
        ]
        
        return VPCConfig(
            name=f"{self.project_name}-vpc-{self.environment}",
            cidr_block="10.0.0.0/16",
            description=f"VPC for {self.project_name} {self.environment} environment",
            subnets=subnets
        )
    
    def create_security_groups(self) -> List[SecurityGroupConfig]:
        """Create security groups for different tiers"""
        
        # ALB Security Group
        alb_sg = SecurityGroupConfig(
            name=f"{self.project_name}-alb-sg",
            description="Security group for Application Load Balancer",
            rules=[
                SecurityGroupRule("ingress", "tcp", "80/80", "0.0.0.0/0", "HTTP from internet", 1),
                SecurityGroupRule("ingress", "tcp", "443/443", "0.0.0.0/0", "HTTPS from internet", 1),
                SecurityGroupRule("egress", "all", "-1/-1", "0.0.0.0/0", "All outbound", 1)
            ]
        )
        
        # Application Security Group  
        app_sg = SecurityGroupConfig(
            name=f"{self.project_name}-app-sg",
            description="Security group for application servers",
            rules=[
                SecurityGroupRule("ingress", "tcp", "8000/8000", "10.0.0.0/16", "API from ALB", 1),
                SecurityGroupRule("ingress", "tcp", "22/22", "10.0.0.0/16", "SSH from bastion", 2),
                SecurityGroupRule("ingress", "tcp", "9090/9090", "10.0.0.0/16", "Metrics collection", 3),
                SecurityGroupRule("egress", "tcp", "3306/3306", "10.0.0.0/16", "MySQL access", 1),
                SecurityGroupRule("egress", "tcp", "6379/6379", "10.0.0.0/16", "Redis access", 1),
                SecurityGroupRule("egress", "tcp", "443/443", "0.0.0.0/0", "HTTPS outbound", 1),
                SecurityGroupRule("egress", "tcp", "80/80", "0.0.0.0/0", "HTTP outbound", 1)
            ]
        )
        
        # Database Security Group
        db_sg = SecurityGroupConfig(
            name=f"{self.project_name}-db-sg", 
            description="Security group for database services",
            rules=[
                SecurityGroupRule("ingress", "tcp", "3306/3306", "10.0.11.0/24", "MySQL from app subnet A", 1),
                SecurityGroupRule("ingress", "tcp", "3306/3306", "10.0.12.0/24", "MySQL from app subnet B", 1),
                SecurityGroupRule("ingress", "tcp", "6379/6379", "10.0.11.0/24", "Redis from app subnet A", 1),
                SecurityGroupRule("ingress", "tcp", "6379/6379", "10.0.12.0/24", "Redis from app subnet B", 1)
            ]
        )
        
        # Bastion Security Group
        bastion_sg = SecurityGroupConfig(
            name=f"{self.project_name}-bastion-sg",
            description="Security group for bastion host",
            rules=[
                SecurityGroupRule("ingress", "tcp", "22/22", "0.0.0.0/0", "SSH from internet", 1),
                SecurityGroupRule("egress", "tcp", "22/22", "10.0.0.0/16", "SSH to private instances", 1),
                SecurityGroupRule("egress", "tcp", "3306/3306", "10.0.0.0/16", "MySQL management", 1)
            ]
        )
        
        return [alb_sg, app_sg, db_sg, bastion_sg]
    
    def generate_terraform_config(self) -> str:
        """Generate complete Terraform configuration"""
        vpc_config = self.create_vpc_config()
        security_groups = self.create_security_groups()
        
        terraform_config = f"""
# Alibaba Cloud Infrastructure Foundation
# Generated for {self.project_name} - {self.environment} environment

terraform {{
  required_providers {{
    alicloud = {{
      source  = "aliyun/alicloud"
      version = "~> 1.190.0"
    }}
  }}
}}

# Configure Alibaba Cloud Provider
provider "alicloud" {{
  region = "{self.region}"
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

# Data sources
data "alicloud_zones" "available" {{
  available_resource_creation = "VSwitch"
}}

# VPC
resource "alicloud_vpc" "main" {{
  vpc_name   = "{vpc_config.name}"
  cidr_block = "{vpc_config.cidr_block}"
  
  tags = {{
    Name        = "{vpc_config.name}"
    Environment = var.environment
    Project     = var.project_name
    Description = "{vpc_config.description}"
  }}
}}

# Internet Gateway
resource "alicloud_nat_gateway" "main" {{
  vpc_id               = alicloud_vpc.main.id
  nat_gateway_name     = "${{var.project_name}}-nat-gateway-${{var.environment}}"
  payment_type         = "PayAsYouGo"
  vswitch_id          = alicloud_vswitch.public_a.id
  nat_type            = "Enhanced"
  
  tags = {{
    Name        = "${{var.project_name}}-nat-gateway-${{var.environment}}"
    Environment = var.environment
    Project     = var.project_name
  }}
}}

# Elastic IP for NAT Gateway
resource "alicloud_eip_address" "nat_gateway" {{
  address_name         = "${{var.project_name}}-nat-eip-${{var.environment}}"
  isp                 = "BGP"
  internet_charge_type = "PayByBandwidth"
  bandwidth           = "100"
  
  tags = {{
    Name        = "${{var.project_name}}-nat-eip-${{var.environment}}"
    Environment = var.environment
    Project     = var.project_name
  }}
}}

# Associate EIP with NAT Gateway
resource "alicloud_eip_association" "nat_gateway" {{
  allocation_id = alicloud_eip_address.nat_gateway.id
  instance_id   = alicloud_nat_gateway.main.id
}}

# Subnets
"""
        
        # Generate subnets
        for subnet in vpc_config.subnets:
            subnet_name_tf = subnet.name.replace("-", "_")
            terraform_config += f"""
resource "alicloud_vswitch" "{subnet_name_tf}" {{
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "{subnet.cidr_block}"
  zone_id      = "{subnet.zone_id}"
  vswitch_name = "{subnet.name}"
  
  tags = {{
    Name        = "{subnet.name}"
    Environment = var.environment
    Project     = var.project_name
    Type        = "{subnet.type}"
    Description = "{subnet.description}"
  }}
}}
"""
        
        # Route tables for private subnets
        terraform_config += """
# Route Table for Private Subnets
resource "alicloud_route_table" "private" {
  vpc_id           = alicloud_vpc.main.id
  route_table_name = "${var.project_name}-private-rt-${var.environment}"
  description      = "Route table for private subnets"
  
  tags = {
    Name        = "${var.project_name}-private-rt-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Route for private subnets to NAT Gateway
resource "alicloud_route_entry" "private_nat" {
  route_table_id        = alicloud_route_table.private.id
  destination_cidrblock = "0.0.0.0/0"
  nexthop_type         = "NatGateway"
  nexthop_id           = alicloud_nat_gateway.main.id
}

# Associate private subnets with route table
resource "alicloud_route_table_attachment" "private_app_a" {
  vswitch_id     = alicloud_vswitch.bailian_demo_private_app_subnet_a.id
  route_table_id = alicloud_route_table.private.id
}

resource "alicloud_route_table_attachment" "private_app_b" {
  vswitch_id     = alicloud_vswitch.bailian_demo_private_app_subnet_b.id
  route_table_id = alicloud_route_table.private.id
}

resource "alicloud_route_table_attachment" "private_db_a" {
  vswitch_id     = alicloud_vswitch.bailian_demo_private_db_subnet_a.id
  route_table_id = alicloud_route_table.private.id
}

resource "alicloud_route_table_attachment" "private_db_b" {
  vswitch_id     = alicloud_vswitch.bailian_demo_private_db_subnet_b.id
  route_table_id = alicloud_route_table.private.id
}

# SNAT entries for private subnets
resource "alicloud_snat_entry" "private_app_a" {
  depends_on        = [alicloud_eip_association.nat_gateway]
  snat_table_id     = alicloud_nat_gateway.main.snat_table_ids
  source_vswitch_id = alicloud_vswitch.bailian_demo_private_app_subnet_a.id
  snat_ip          = alicloud_eip_address.nat_gateway.ip_address
}

resource "alicloud_snat_entry" "private_app_b" {
  depends_on        = [alicloud_eip_association.nat_gateway]
  snat_table_id     = alicloud_nat_gateway.main.snat_table_ids
  source_vswitch_id = alicloud_vswitch.bailian_demo_private_app_subnet_b.id
  snat_ip          = alicloud_eip_address.nat_gateway.ip_address
}

# Security Groups
"""
        
        # Generate security groups
        for sg in security_groups:
            sg_name_tf = sg.name.replace("-", "_")
            terraform_config += f"""
resource "alicloud_security_group" "{sg_name_tf}" {{
  name        = "{sg.name}"
  description = "{sg.description}"
  vpc_id      = alicloud_vpc.main.id
  
  tags = {{
    Name        = "{sg.name}"
    Environment = var.environment
    Project     = var.project_name
  }}
}}
"""
            
            # Generate security group rules
            for i, rule in enumerate(sg.rules):
                rule_name = f"{sg_name_tf}_rule_{i}"
                terraform_config += f"""
resource "alicloud_security_group_rule" "{rule_name}" {{
  type              = "{rule.type}"
  ip_protocol       = "{rule.protocol}"
  port_range        = "{rule.port_range}"
  security_group_id = alicloud_security_group.{sg_name_tf}.id
  cidr_ip          = "{rule.source_cidr}"
  description      = "{rule.description}"
  priority         = {rule.priority}
}}
"""
        
        # Network ACLs for additional security
        terraform_config += f"""
# Network ACL for database subnets
resource "alicloud_network_acl" "database" {{
  vpc_id           = alicloud_vpc.main.id
  network_acl_name = "${{var.project_name}}-db-nacl-${{var.environment}}"
  description      = "Network ACL for database subnets"
  
  tags = {{
    Name        = "${{var.project_name}}-db-nacl-${{var.environment}}"
    Environment = var.environment
    Project     = var.project_name
  }}
}}

# Database NACL Rules
resource "alicloud_network_acl_entries" "database" {{
  network_acl_id = alicloud_network_acl.database.id
  
  ingress {{
    protocol         = "tcp"
    rule_action      = "accept"
    port             = "3306/3306"
    source_cidr_ip   = "10.0.11.0/24"
    description      = "MySQL from app subnet A"
    priority         = 1
  }}
  
  ingress {{
    protocol         = "tcp"
    rule_action      = "accept"
    port             = "3306/3306"
    source_cidr_ip   = "10.0.12.0/24"
    description      = "MySQL from app subnet B"
    priority         = 2
  }}
  
  ingress {{
    protocol         = "tcp"
    rule_action      = "accept"
    port             = "6379/6379"
    source_cidr_ip   = "10.0.11.0/24"
    description      = "Redis from app subnet A"
    priority         = 3
  }}
  
  ingress {{
    protocol         = "tcp"
    rule_action      = "accept"
    port             = "6379/6379"
    source_cidr_ip   = "10.0.12.0/24"
    description      = "Redis from app subnet B"
    priority         = 4
  }}
  
  egress {{
    protocol         = "all"
    rule_action      = "accept"
    port             = "-1/-1"
    destination_cidr_ip = "0.0.0.0/0"
    description      = "Allow all outbound"
    priority         = 1
  }}
}}

# Associate NACL with database subnets
resource "alicloud_network_acl_attachment" "db_subnet_a" {{
  network_acl_id = alicloud_network_acl.database.id
  resource_id    = alicloud_vswitch.bailian_demo_private_db_subnet_a.id
  resource_type  = "VSwitch"
}}

resource "alicloud_network_acl_attachment" "db_subnet_b" {{
  network_acl_id = alicloud_network_acl.database.id
  resource_id    = alicloud_vswitch.bailian_demo_private_db_subnet_b.id
  resource_type  = "VSwitch"
}}

# Outputs
output "vpc_id" {{
  description = "ID of the VPC"
  value       = alicloud_vpc.main.id
}}

output "vpc_cidr_block" {{
  description = "CIDR block of the VPC"
  value       = alicloud_vpc.main.cidr_block
}}

output "public_subnet_ids" {{
  description = "IDs of public subnets"
  value = [
    alicloud_vswitch.bailian_demo_public_subnet_a.id,
    alicloud_vswitch.bailian_demo_public_subnet_b.id
  ]
}}

output "private_app_subnet_ids" {{
  description = "IDs of private application subnets"
  value = [
    alicloud_vswitch.bailian_demo_private_app_subnet_a.id,  
    alicloud_vswitch.bailian_demo_private_app_subnet_b.id
  ]
}}

output "private_db_subnet_ids" {{
  description = "IDs of private database subnets"
  value = [
    alicloud_vswitch.bailian_demo_private_db_subnet_a.id,
    alicloud_vswitch.bailian_demo_private_db_subnet_b.id
  ]
}}

output "security_group_ids" {{
  description = "IDs of security groups"
  value = {{
"""
        
        for sg in security_groups:
            sg_name_tf = sg.name.replace("-", "_")
            terraform_config += f'    "{sg.name}" = alicloud_security_group.{sg_name_tf}.id\n'
        
        terraform_config += """  }
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = alicloud_nat_gateway.main.id
}

output "nat_gateway_eip" {
  description = "Public IP of the NAT Gateway"
  value       = alicloud_eip_address.nat_gateway.ip_address
}
"""
        
        return terraform_config
    
    def generate_deployment_script(self) -> str:
        """Generate infrastructure deployment script"""
        return f"""#!/bin/bash
# Infrastructure Foundation Deployment Script
set -e

echo "🏗️  Deploying Infrastructure Foundation for {self.project_name}..."

# Variables
export ENVIRONMENT="{self.environment}"
export PROJECT_NAME="{self.project_name}"
export REGION="{self.region}"

# Check prerequisites
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ Error: Alibaba Cloud credentials not set"
    exit 1
fi

# Initialize Terraform
echo "📋 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan infrastructure deployment
echo "📊 Planning infrastructure deployment..."
terraform plan -var="environment=$ENVIRONMENT" \\
               -var="project_name=$PROJECT_NAME" \\
               -out=infrastructure-plan

# Apply infrastructure
echo "🚀 Applying infrastructure configuration..."
terraform apply infrastructure-plan

# Get outputs
echo "📋 Infrastructure deployment completed!"
echo "VPC ID: $(terraform output -raw vpc_id)"
echo "VPC CIDR: $(terraform output -raw vpc_cidr_block)"
echo "NAT Gateway IP: $(terraform output -raw nat_gateway_eip)"

# Validate connectivity  
echo "🔍 Validating infrastructure..."
VPC_ID=$(terraform output -raw vpc_id)
echo "VPC $VPC_ID created successfully"

# List created resources
echo "📊 Created Resources Summary:"
echo "- VPC: 1"
echo "- Subnets: 6 (2 public, 4 private)"
echo "- Security Groups: 4"
echo "- NAT Gateway: 1"
echo "- Route Tables: 1"
echo "- Network ACLs: 1"

echo "🎉 Infrastructure foundation deployment completed successfully!"
"""

def main():
    """Generate infrastructure foundation configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate infrastructure foundation")
    parser.add_argument("--environment", default="production", help="Environment name")
    parser.add_argument("--region", default="cn-hangzhou", help="Alibaba Cloud region")
    
    args = parser.parse_args()
    
    generator = InfrastructureFoundationGenerator(args.environment, args.region)
    
    # Generate configurations
    terraform_config = generator.generate_terraform_config()
    deployment_script = generator.generate_deployment_script()
    
    # Save configurations
    with open("infrastructure_terraform.tf", "w") as f:
        f.write(terraform_config)
    
    with open("deploy_infrastructure.sh", "w") as f:
        f.write(deployment_script)
    
    # Make deployment script executable
    import os
    os.chmod("deploy_infrastructure.sh", 0o755)
    
    print("✅ Infrastructure foundation files generated:")
    print("  - infrastructure_terraform.tf (Terraform configuration)")
    print("  - deploy_infrastructure.sh (Deployment script)")
    print(f"  - Environment: {args.environment}")
    print(f"  - Region: {args.region}")

if __name__ == "__main__":
    main()