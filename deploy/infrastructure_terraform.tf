
# Alibaba Cloud Infrastructure Foundation
# Generated for bailian-demo - production environment

terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.190.0"
    }
  }
}

# Configure Alibaba Cloud Provider
provider "alicloud" {
  region = "cn-hangzhou"
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

# Data sources
data "alicloud_zones" "available" {
  available_resource_creation = "VSwitch"
}

# VPC
resource "alicloud_vpc" "main" {
  vpc_name   = "bailian-demo-vpc-production"
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name        = "bailian-demo-vpc-production"
    Environment = var.environment
    Project     = var.project_name
    Description = "VPC for bailian-demo production environment"
  }
}

# Internet Gateway
resource "alicloud_nat_gateway" "main" {
  vpc_id               = alicloud_vpc.main.id
  nat_gateway_name     = "${var.project_name}-nat-gateway-${var.environment}"
  payment_type         = "PayAsYouGo"
  vswitch_id          = alicloud_vswitch.public_a.id
  nat_type            = "Enhanced"
  
  tags = {
    Name        = "${var.project_name}-nat-gateway-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Elastic IP for NAT Gateway
resource "alicloud_eip_address" "nat_gateway" {
  address_name         = "${var.project_name}-nat-eip-${var.environment}"
  isp                 = "BGP"
  internet_charge_type = "PayByBandwidth"
  bandwidth           = "100"
  
  tags = {
    Name        = "${var.project_name}-nat-eip-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Associate EIP with NAT Gateway
resource "alicloud_eip_association" "nat_gateway" {
  allocation_id = alicloud_eip_address.nat_gateway.id
  instance_id   = alicloud_nat_gateway.main.id
}

# Subnets

resource "alicloud_vswitch" "bailian_demo_public_subnet_a" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.1.0/24"
  zone_id      = "cn-hangzhou-h"
  vswitch_name = "bailian-demo-public-subnet-a"
  
  tags = {
    Name        = "bailian-demo-public-subnet-a"
    Environment = var.environment
    Project     = var.project_name
    Type        = "public"
    Description = "Public subnet for load balancers in AZ-A"
  }
}

resource "alicloud_vswitch" "bailian_demo_public_subnet_b" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.2.0/24"
  zone_id      = "cn-hangzhou-i"
  vswitch_name = "bailian-demo-public-subnet-b"
  
  tags = {
    Name        = "bailian-demo-public-subnet-b"
    Environment = var.environment
    Project     = var.project_name
    Type        = "public"
    Description = "Public subnet for load balancers in AZ-B"
  }
}

resource "alicloud_vswitch" "bailian_demo_private_app_subnet_a" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.11.0/24"
  zone_id      = "cn-hangzhou-h"
  vswitch_name = "bailian-demo-private-app-subnet-a"
  
  tags = {
    Name        = "bailian-demo-private-app-subnet-a"
    Environment = var.environment
    Project     = var.project_name
    Type        = "private"
    Description = "Private subnet for application servers in AZ-A"
  }
}

resource "alicloud_vswitch" "bailian_demo_private_app_subnet_b" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.12.0/24"
  zone_id      = "cn-hangzhou-i"
  vswitch_name = "bailian-demo-private-app-subnet-b"
  
  tags = {
    Name        = "bailian-demo-private-app-subnet-b"
    Environment = var.environment
    Project     = var.project_name
    Type        = "private"
    Description = "Private subnet for application servers in AZ-B"
  }
}

resource "alicloud_vswitch" "bailian_demo_private_db_subnet_a" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.21.0/24"
  zone_id      = "cn-hangzhou-h"
  vswitch_name = "bailian-demo-private-db-subnet-a"
  
  tags = {
    Name        = "bailian-demo-private-db-subnet-a"
    Environment = var.environment
    Project     = var.project_name
    Type        = "private"
    Description = "Private subnet for databases in AZ-A"
  }
}

resource "alicloud_vswitch" "bailian_demo_private_db_subnet_b" {
  vpc_id       = alicloud_vpc.main.id
  cidr_block   = "10.0.22.0/24"
  zone_id      = "cn-hangzhou-i"
  vswitch_name = "bailian-demo-private-db-subnet-b"
  
  tags = {
    Name        = "bailian-demo-private-db-subnet-b"
    Environment = var.environment
    Project     = var.project_name
    Type        = "private"
    Description = "Private subnet for databases in AZ-B"
  }
}

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

resource "alicloud_security_group" "bailian_demo_alb_sg" {
  name        = "bailian-demo-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = alicloud_vpc.main.id
  
  tags = {
    Name        = "bailian-demo-alb-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "alicloud_security_group_rule" "bailian_demo_alb_sg_rule_0" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "80/80"
  security_group_id = alicloud_security_group.bailian_demo_alb_sg.id
  cidr_ip          = "0.0.0.0/0"
  description      = "HTTP from internet"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_alb_sg_rule_1" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "443/443"
  security_group_id = alicloud_security_group.bailian_demo_alb_sg.id
  cidr_ip          = "0.0.0.0/0"
  description      = "HTTPS from internet"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_alb_sg_rule_2" {
  type              = "egress"
  ip_protocol       = "all"
  port_range        = "-1/-1"
  security_group_id = alicloud_security_group.bailian_demo_alb_sg.id
  cidr_ip          = "0.0.0.0/0"
  description      = "All outbound"
  priority         = 1
}

resource "alicloud_security_group" "bailian_demo_app_sg" {
  name        = "bailian-demo-app-sg"
  description = "Security group for application servers"
  vpc_id      = alicloud_vpc.main.id
  
  tags = {
    Name        = "bailian-demo-app-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_rule_0" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "8000/8000"
  security_group_id = alicloud_security_group.bailian_demo_app_sg.id
  cidr_ip          = "10.0.0.0/16"
  description      = "API from ALB"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_rule_1" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "22/22"
  security_group_id = alicloud_security_group.bailian_demo_app_sg.id
  cidr_ip          = "10.0.0.0/16"
  description      = "SSH from bastion"
  priority         = 2
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_rule_2" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "9090/9090"
  security_group_id = alicloud_security_group.bailian_demo_app_sg.id
  cidr_ip          = "10.0.0.0/16"
  description      = "Metrics collection"
  priority         = 3
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_rule_3" {
  type              = "egress"
  ip_protocol       = "tcp"
  port_range        = "3306/3306"
  security_group_id = alicloud_security_group.bailian_demo_app_sg.id
  cidr_ip          = "10.0.0.0/16"
  description      = "MySQL access"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_rule_4" {
  type              = "egress"
  ip_protocol       = "tcp"
  port_range        = "6379/6379"
  security_group_id = alicloud_security_group.bailian_demo_app_sg.id
  cidr_ip          = "10.0.0.0/16"
  description      = "Redis access"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_rule_5" {
  type              = "egress"
  ip_protocol       = "tcp"
  port_range        = "443/443"
  security_group_id = alicloud_security_group.bailian_demo_app_sg.id
  cidr_ip          = "0.0.0.0/0"
  description      = "HTTPS outbound"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_rule_6" {
  type              = "egress"
  ip_protocol       = "tcp"
  port_range        = "80/80"
  security_group_id = alicloud_security_group.bailian_demo_app_sg.id
  cidr_ip          = "0.0.0.0/0"
  description      = "HTTP outbound"
  priority         = 1
}

resource "alicloud_security_group" "bailian_demo_db_sg" {
  name        = "bailian-demo-db-sg"
  description = "Security group for database services"
  vpc_id      = alicloud_vpc.main.id
  
  tags = {
    Name        = "bailian-demo-db-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "alicloud_security_group_rule" "bailian_demo_db_sg_rule_0" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "3306/3306"
  security_group_id = alicloud_security_group.bailian_demo_db_sg.id
  cidr_ip          = "10.0.11.0/24"
  description      = "MySQL from app subnet A"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_db_sg_rule_1" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "3306/3306"
  security_group_id = alicloud_security_group.bailian_demo_db_sg.id
  cidr_ip          = "10.0.12.0/24"
  description      = "MySQL from app subnet B"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_db_sg_rule_2" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "6379/6379"
  security_group_id = alicloud_security_group.bailian_demo_db_sg.id
  cidr_ip          = "10.0.11.0/24"
  description      = "Redis from app subnet A"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_db_sg_rule_3" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "6379/6379"
  security_group_id = alicloud_security_group.bailian_demo_db_sg.id
  cidr_ip          = "10.0.12.0/24"
  description      = "Redis from app subnet B"
  priority         = 1
}

resource "alicloud_security_group" "bailian_demo_bastion_sg" {
  name        = "bailian-demo-bastion-sg"
  description = "Security group for bastion host"
  vpc_id      = alicloud_vpc.main.id
  
  tags = {
    Name        = "bailian-demo-bastion-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "alicloud_security_group_rule" "bailian_demo_bastion_sg_rule_0" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "22/22"
  security_group_id = alicloud_security_group.bailian_demo_bastion_sg.id
  cidr_ip          = "0.0.0.0/0"
  description      = "SSH from internet"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_bastion_sg_rule_1" {
  type              = "egress"
  ip_protocol       = "tcp"
  port_range        = "22/22"
  security_group_id = alicloud_security_group.bailian_demo_bastion_sg.id
  cidr_ip          = "10.0.0.0/16"
  description      = "SSH to private instances"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_bastion_sg_rule_2" {
  type              = "egress"
  ip_protocol       = "tcp"
  port_range        = "3306/3306"
  security_group_id = alicloud_security_group.bailian_demo_bastion_sg.id
  cidr_ip          = "10.0.0.0/16"
  description      = "MySQL management"
  priority         = 1
}

# Network ACL for database subnets
resource "alicloud_network_acl" "database" {
  vpc_id           = alicloud_vpc.main.id
  network_acl_name = "${var.project_name}-db-nacl-${var.environment}"
  description      = "Network ACL for database subnets"
  
  tags = {
    Name        = "${var.project_name}-db-nacl-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Database NACL Rules
resource "alicloud_network_acl_entries" "database" {
  network_acl_id = alicloud_network_acl.database.id
  
  ingress {
    protocol         = "tcp"
    rule_action      = "accept"
    port             = "3306/3306"
    source_cidr_ip   = "10.0.11.0/24"
    description      = "MySQL from app subnet A"
    priority         = 1
  }
  
  ingress {
    protocol         = "tcp"
    rule_action      = "accept"
    port             = "3306/3306"
    source_cidr_ip   = "10.0.12.0/24"
    description      = "MySQL from app subnet B"
    priority         = 2
  }
  
  ingress {
    protocol         = "tcp"
    rule_action      = "accept"
    port             = "6379/6379"
    source_cidr_ip   = "10.0.11.0/24"
    description      = "Redis from app subnet A"
    priority         = 3
  }
  
  ingress {
    protocol         = "tcp"
    rule_action      = "accept"
    port             = "6379/6379"
    source_cidr_ip   = "10.0.12.0/24"
    description      = "Redis from app subnet B"
    priority         = 4
  }
  
  egress {
    protocol         = "all"
    rule_action      = "accept"
    port             = "-1/-1"
    destination_cidr_ip = "0.0.0.0/0"
    description      = "Allow all outbound"
    priority         = 1
  }
}

# Associate NACL with database subnets
resource "alicloud_network_acl_attachment" "db_subnet_a" {
  network_acl_id = alicloud_network_acl.database.id
  resource_id    = alicloud_vswitch.bailian_demo_private_db_subnet_a.id
  resource_type  = "VSwitch"
}

resource "alicloud_network_acl_attachment" "db_subnet_b" {
  network_acl_id = alicloud_network_acl.database.id
  resource_id    = alicloud_vswitch.bailian_demo_private_db_subnet_b.id
  resource_type  = "VSwitch"
}

# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = alicloud_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = alicloud_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value = [
    alicloud_vswitch.bailian_demo_public_subnet_a.id,
    alicloud_vswitch.bailian_demo_public_subnet_b.id
  ]
}

output "private_app_subnet_ids" {
  description = "IDs of private application subnets"
  value = [
    alicloud_vswitch.bailian_demo_private_app_subnet_a.id,  
    alicloud_vswitch.bailian_demo_private_app_subnet_b.id
  ]
}

output "private_db_subnet_ids" {
  description = "IDs of private database subnets"
  value = [
    alicloud_vswitch.bailian_demo_private_db_subnet_a.id,
    alicloud_vswitch.bailian_demo_private_db_subnet_b.id
  ]
}

output "security_group_ids" {
  description = "IDs of security groups"
  value = {
    "bailian-demo-alb-sg" = alicloud_security_group.bailian_demo_alb_sg.id
    "bailian-demo-app-sg" = alicloud_security_group.bailian_demo_app_sg.id
    "bailian-demo-db-sg" = alicloud_security_group.bailian_demo_db_sg.id
    "bailian-demo-bastion-sg" = alicloud_security_group.bailian_demo_bastion_sg.id
  }
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = alicloud_nat_gateway.main.id
}

output "nat_gateway_eip" {
  description = "Public IP of the NAT Gateway"
  value       = alicloud_eip_address.nat_gateway.ip_address
}
