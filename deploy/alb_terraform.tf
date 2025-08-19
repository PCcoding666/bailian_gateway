
# Application Load Balancer Configuration
resource "alicloud_alb_load_balancer" "bailian_alb" {
  load_balancer_name = "bailian-demo-alb-production"
  load_balancer_type = "application"
  scheme             = "internet-facing"
  vpc_id            = "vpc-xxxxxxxxx"
  
  zone_mappings {
    zone_id    = data.alicloud_zones.default.zones[0].id
    subnet_id  = "vsw-xxxxxxxxx"
  }
  
  zone_mappings {
    zone_id    = data.alicloud_zones.default.zones[1].id
    subnet_id  = "vsw-yyyyyyyyy"
  }
  
  security_group_ids = ["sg-xxxxxxxxx"]
  
  tags = {
    "Environment": "production",
    "Project": "bailian-demo",
    "ManagedBy": "terraform",
    "Component": "load-balancer"
}
}

# Target Groups

resource "alicloud_alb_server_group" "bailian_backend_tg_production" {
  server_group_name = "bailian-backend-tg-production"
  vpc_id           = "vpc-xxxxxxxxx"
  protocol         = "HTTP"
  
  health_check_config {
    health_check_enabled         = true
    health_check_protocol        = "HTTP"
    health_check_port           = 8000
    health_check_path           = "/health/ready"
    health_check_interval       = 30
    health_check_timeout        = 5
    unhealthy_threshold         = 3
    healthy_threshold           = 2
    health_check_http_codes     = ["200"]
  }
  
  tags = {"Environment": "production", "Project": "bailian-demo", "ManagedBy": "terraform", "Component": "load-balancer"}
}

resource "alicloud_alb_server_group" "bailian_metrics_tg_production" {
  server_group_name = "bailian-metrics-tg-production"
  vpc_id           = "vpc-xxxxxxxxx"
  protocol         = "HTTP"
  
  health_check_config {
    health_check_enabled         = true
    health_check_protocol        = "HTTP"
    health_check_port           = 8000
    health_check_path           = "/metrics"
    health_check_interval       = 60
    health_check_timeout        = 10
    unhealthy_threshold         = 2
    healthy_threshold           = 2
    health_check_http_codes     = ["200"]
  }
  
  tags = {"Environment": "production", "Project": "bailian-demo", "ManagedBy": "terraform", "Component": "load-balancer"}
}

resource "alicloud_alb_listener" "bailian_demo_alb_production_listener_80" {
  load_balancer_id = alicloud_alb_load_balancer.bailian_alb.id
  listener_protocol = "HTTP"
  listener_port    = 80
  
  default_actions {
    type = "Redirect"
    redirect_config {
      protocol    = "HTTPS"
      port        = "443"
      http_code   = "HTTP_301"
    }
  }
}

resource "alicloud_alb_listener" "bailian_demo_alb_production_listener_443" {
  load_balancer_id = alicloud_alb_load_balancer.bailian_alb.id
  listener_protocol = "HTTPS"
  listener_port    = 443
  
  default_actions {
    type = "ForwardGroup"
    forward_group_config {
      server_group_tuples {
        server_group_id = alicloud_alb_server_group.bailian_backend_tg_production.id
      }
    }
  }
}

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
    "bailian-backend-tg-production" = alicloud_alb_server_group.bailian_backend_tg_production.id
    "bailian-metrics-tg-production" = alicloud_alb_server_group.bailian_metrics_tg_production.id
  }
}
