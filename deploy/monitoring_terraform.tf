
# CloudMonitor Configuration for bailian-demo

resource "alicloud_cms_alarm_contact_group" "main" {
  alarm_contact_group_name = "bailian-demo-alerts-production"
  describe                 = "Alert contact group for bailian-demo"
  contacts                 = ["admin@example.com"]
}

# Alert Rules

resource "alicloud_cms_alarm" "bailian_demo_high_error_rate" {
  name         = "bailian-demo-high-error-rate"
  project      = "acs_ecs_dashboard"
  metric       = "http_errors_rate"
  dimensions   = {"instanceId": "i-*"}
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "5.0"
  triggered_count = 3
  contact_groups = [alicloud_cms_alarm_contact_group.main.id]
  enabled      = true
}

resource "alicloud_cms_alarm" "bailian_demo_high_cpu" {
  name         = "bailian-demo-high-cpu"
  project      = "acs_ecs_dashboard"
  metric       = "CPUUtilization"
  dimensions   = {"instanceId": "i-*"}
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "80.0"
  triggered_count = 3
  contact_groups = [alicloud_cms_alarm_contact_group.main.id]
  enabled      = true
}

resource "alicloud_cms_alarm" "bailian_demo_high_memory" {
  name         = "bailian-demo-high-memory"
  project      = "acs_ecs_dashboard"
  metric       = "MemoryUtilization"
  dimensions   = {"instanceId": "i-*"}
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "85.0"
  triggered_count = 3
  contact_groups = [alicloud_cms_alarm_contact_group.main.id]
  enabled      = true
}

resource "alicloud_cms_alarm" "bailian_demo_db_connections" {
  name         = "bailian-demo-db-connections"
  project      = "acs_rds_dashboard"
  metric       = "ConnectionUsage"
  dimensions   = {"instanceId": "rm-*"}
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "80.0"
  triggered_count = 3
  contact_groups = [alicloud_cms_alarm_contact_group.main.id]
  enabled      = true
}

resource "alicloud_cms_alarm" "bailian_demo_ai_latency" {
  name         = "bailian-demo-ai-latency"
  project      = "acs_customMetric"
  metric       = "ai_request_duration"
  dimensions   = {"service": "bailian"}
  statistics   = "Average"
  period       = 300
  operator     = "GreaterThanThreshold"
  threshold    = "5000.0"
  triggered_count = 3
  contact_groups = [alicloud_cms_alarm_contact_group.main.id]
  enabled      = true
}

# Dashboard
resource "alicloud_cms_group_metric_rule" "dashboard_rules" {
  group_id    = alicloud_cms_monitor_group.main.id
  rule_name   = "bailian-demo-monitoring-production"
  category    = "ecs"
  metric_name = "CPUUtilization"
  namespace   = "acs_ecs_dashboard"
  
  escalations_critical {
    comparison_operator = "GreaterThanThreshold"
    statistics         = "Average"
    threshold          = "90"
    times              = 3
  }
}

resource "alicloud_cms_monitor_group" "main" {
  monitor_group_name = "bailian-demo-group-production"
  contact_groups     = [alicloud_cms_alarm_contact_group.main.alarm_contact_group_name]
}
