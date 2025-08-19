
# Alibaba Cloud Security Configuration
# Generated for bailian-demo - production environment

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

variable "domain" {
  description = "Domain name for SSL and WAF"
  type        = string
  default     = "bailian-demo.example.com"
}

# Data sources
data "alicloud_vpcs" "default" {
  name_regex = "default"
}

# RAM Roles

resource "alicloud_ram_role" "bailian_demo_ecs_role_production" {
  name        = "bailian-demo-ecs-role-production"
  description = "ECS service role for Bailian Demo backend services"
  document    = jsonencode({
    "Version": "1",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "ecs.aliyuncs.com"
                ]
            },
            "Action": [
                "sts:AssumeRole"
            ]
        }
    ]
})
  
  tags = {
    "Environment": "production",
    "Project": "bailian-demo",
    "Component": "backend"
}
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_ecs_role_production_policy_0" {
  role_name   = alicloud_ram_role.bailian_demo_ecs_role_production.name
  policy_name = "AliyunRDSReadOnlyAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_ecs_role_production_policy_1" {
  role_name   = alicloud_ram_role.bailian_demo_ecs_role_production.name
  policy_name = "AliyunKvstoreReadOnlyAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_ecs_role_production_policy_2" {
  role_name   = alicloud_ram_role.bailian_demo_ecs_role_production.name
  policy_name = "AliyunOSSReadOnlyAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_ecs_role_production_policy_3" {
  role_name   = alicloud_ram_role.bailian_demo_ecs_role_production.name
  policy_name = "AliyunLogReadOnlyAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_ecs_role_production_policy_4" {
  role_name   = alicloud_ram_role.bailian_demo_ecs_role_production.name
  policy_name = "AliyunCloudMonitorReadOnlyAccess"
  policy_type = "System"
}

resource "alicloud_ram_role" "bailian_demo_fc_role_production" {
  name        = "bailian-demo-fc-role-production"
  description = "Function Compute role for AI processing"
  document    = jsonencode({
    "Version": "1",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "fc.aliyuncs.com"
                ]
            },
            "Action": [
                "sts:AssumeRole"
            ]
        }
    ]
})
  
  tags = {
    "Environment": "production",
    "Project": "bailian-demo",
    "Component": "function-compute"
}
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_fc_role_production_policy_0" {
  role_name   = alicloud_ram_role.bailian_demo_fc_role_production.name
  policy_name = "AliyunLogFullAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_fc_role_production_policy_1" {
  role_name   = alicloud_ram_role.bailian_demo_fc_role_production.name
  policy_name = "AliyunOSSReadOnlyAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_fc_role_production_policy_2" {
  role_name   = alicloud_ram_role.bailian_demo_fc_role_production.name
  policy_name = "AliyunRDSReadOnlyAccess"
  policy_type = "System"
}

resource "alicloud_ram_role" "bailian_demo_cr_role_production" {
  name        = "bailian-demo-cr-role-production"
  description = "Container Registry access role"
  document    = jsonencode({
    "Version": "1",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "ack.aliyuncs.com"
                ]
            },
            "Action": [
                "sts:AssumeRole"
            ]
        }
    ]
})
  
  tags = {
    "Environment": "production",
    "Project": "bailian-demo",
    "Component": "container-registry"
}
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_cr_role_production_policy_0" {
  role_name   = alicloud_ram_role.bailian_demo_cr_role_production.name
  policy_name = "AliyunContainerRegistryFullAccess"
  policy_type = "System"
}

resource "alicloud_ram_role" "bailian_demo_apigateway_role_production" {
  name        = "bailian-demo-apigateway-role-production"
  description = "API Gateway service role"
  document    = jsonencode({
    "Version": "1",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "apigateway.aliyuncs.com"
                ]
            },
            "Action": [
                "sts:AssumeRole"
            ]
        }
    ]
})
  
  tags = {
    "Environment": "production",
    "Project": "bailian-demo",
    "Component": "api-gateway"
}
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_apigateway_role_production_policy_0" {
  role_name   = alicloud_ram_role.bailian_demo_apigateway_role_production.name
  policy_name = "AliyunLogFullAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "bailian_demo_apigateway_role_production_policy_1" {
  role_name   = alicloud_ram_role.bailian_demo_apigateway_role_production.name
  policy_name = "AliyunCloudMonitorFullAccess"
  policy_type = "System"
}

# Security Groups

resource "alicloud_security_group" "bailian_demo_web_sg_production" {
  name        = "bailian-demo-web-sg-production"
  description = "Security group for web tier (ALB)"
  vpc_id      = data.alicloud_vpcs.default.vpcs[0].id
  
  tags = {
    "Environment": "production",
    "Project": "bailian-demo",
    "Tier": "web"
}
}

resource "alicloud_security_group_rule" "bailian_demo_web_sg_production_rule_0" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "80/80"
  security_group_id = alicloud_security_group.bailian_demo_web_sg_production.id
  cidr_ip          = "0.0.0.0/0"
  description      = "HTTP access"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_web_sg_production_rule_1" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "443/443"
  security_group_id = alicloud_security_group.bailian_demo_web_sg_production.id
  cidr_ip          = "0.0.0.0/0"
  description      = "HTTPS access"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_web_sg_production_rule_2" {
  type              = "egress"
  ip_protocol       = "all"
  port_range        = "-1/-1"
  security_group_id = alicloud_security_group.bailian_demo_web_sg_production.id
  cidr_ip          = "0.0.0.0/0"
  description      = "All outbound"
  priority         = 1
}

resource "alicloud_security_group" "bailian_demo_app_sg_production" {
  name        = "bailian-demo-app-sg-production"
  description = "Security group for application tier"
  vpc_id      = data.alicloud_vpcs.default.vpcs[0].id
  
  tags = {
    "Environment": "production",
    "Project": "bailian-demo",
    "Tier": "application"
}
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_production_rule_0" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "8000/8000"
  security_group_id = alicloud_security_group.bailian_demo_app_sg_production.id
  cidr_ip          = "10.0.0.0/8"
  description      = "Backend API"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_production_rule_1" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "22/22"
  security_group_id = alicloud_security_group.bailian_demo_app_sg_production.id
  cidr_ip          = "10.0.0.0/8"
  description      = "SSH access"
  priority         = 2
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_production_rule_2" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "9090/9090"
  security_group_id = alicloud_security_group.bailian_demo_app_sg_production.id
  cidr_ip          = "10.0.0.0/8"
  description      = "Metrics"
  priority         = 3
}

resource "alicloud_security_group_rule" "bailian_demo_app_sg_production_rule_3" {
  type              = "egress"
  ip_protocol       = "all"
  port_range        = "-1/-1"
  security_group_id = alicloud_security_group.bailian_demo_app_sg_production.id
  cidr_ip          = "0.0.0.0/0"
  description      = "All outbound"
  priority         = 1
}

resource "alicloud_security_group" "bailian_demo_db_sg_production" {
  name        = "bailian-demo-db-sg-production"
  description = "Security group for database tier"
  vpc_id      = data.alicloud_vpcs.default.vpcs[0].id
  
  tags = {
    "Environment": "production",
    "Project": "bailian-demo",
    "Tier": "database"
}
}

resource "alicloud_security_group_rule" "bailian_demo_db_sg_production_rule_0" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "3306/3306"
  security_group_id = alicloud_security_group.bailian_demo_db_sg_production.id
  cidr_ip          = "10.0.0.0/8"
  description      = "MySQL access"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_db_sg_production_rule_1" {
  type              = "ingress"
  ip_protocol       = "tcp"
  port_range        = "6379/6379"
  security_group_id = alicloud_security_group.bailian_demo_db_sg_production.id
  cidr_ip          = "10.0.0.0/8"
  description      = "Redis access"
  priority         = 1
}

resource "alicloud_security_group_rule" "bailian_demo_db_sg_production_rule_2" {
  type              = "egress"
  ip_protocol       = "tcp"
  port_range        = "3306/3306"
  security_group_id = alicloud_security_group.bailian_demo_db_sg_production.id
  cidr_ip          = "10.0.0.0/8"
  description      = "MySQL replication"
  priority         = 1
}

# Web Application Firewall
resource "alicloud_waf_instance" "main" {
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
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "alicloud_waf_domain" "main" {
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
}

# WAF Protection Rules
resource "alicloud_waf_protection_module" "cc_protection" {
  domain     = alicloud_waf_domain.main.domain_name
  instance_id = alicloud_waf_instance.main.id
  defense_type = "cc"
  status     = 1
}

resource "alicloud_waf_protection_module" "web_attack" {
  domain     = alicloud_waf_domain.main.domain_name
  instance_id = alicloud_waf_instance.main.id
  defense_type = "waf"
  status     = 1
}

# SSL Certificate
resource "alicloud_ssl_certificates_service_certificate" "main" {
  certificate_name = "bailian-demo-ssl-production"
  cert             = file("path/to/certificate.crt")
  key              = file("path/to/private.key")
}

# Security Center (Cloud Security Center)
resource "alicloud_threat_detection_baseline_strategy" "main" {
  baseline_strategy_name = "bailian-demo-baseline-production"
  custom_type           = "custom"
  end_time             = "08:00:00"
  start_time           = "02:00:00"
  target_type          = "groupId"
  cycle_days           = 3
  cycle_start_time     = 3
}

resource "alicloud_threat_detection_anti_brute_force_rule" "main" {
  name            = "bailian-demo-anti-brute-force"
  forbidden_time  = 360
  fail_count      = 5
  span            = 60
  default_rule    = false
  
  uuid_list = ["all"]  # Apply to all assets
}

# Outputs
output "ram_roles" {
  description = "Created RAM roles"
  value = {
    "bailian-demo-ecs-role-production" = alicloud_ram_role.bailian_demo_ecs_role_production.arn
    "bailian-demo-fc-role-production" = alicloud_ram_role.bailian_demo_fc_role_production.arn
    "bailian-demo-cr-role-production" = alicloud_ram_role.bailian_demo_cr_role_production.arn
    "bailian-demo-apigateway-role-production" = alicloud_ram_role.bailian_demo_apigateway_role_production.arn
  }
}

output "security_groups" {
  description = "Created security groups"
  value = {
    "bailian-demo-web-sg-production" = alicloud_security_group.bailian_demo_web_sg_production.id
    "bailian-demo-app-sg-production" = alicloud_security_group.bailian_demo_app_sg_production.id
    "bailian-demo-db-sg-production" = alicloud_security_group.bailian_demo_db_sg_production.id
  }
}

output "waf_instance_id" {
  description = "WAF instance ID"
  value       = alicloud_waf_instance.main.id
}

output "ssl_certificate_id" {
  description = "SSL certificate ID"
  value       = alicloud_ssl_certificates_service_certificate.main.id
}
