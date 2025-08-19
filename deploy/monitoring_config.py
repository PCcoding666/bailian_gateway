#!/usr/bin/env python3
"""
Alibaba Cloud CloudMonitor Configuration for Bailian Demo
Creates dashboards, alerts, and monitoring rules
"""

import json
import yaml
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_name: str
    metric_name: str
    namespace: str
    dimensions: Dict[str, str]
    comparison_operator: str  # GreaterThanThreshold, LessThanThreshold, etc.
    threshold: float
    evaluation_periods: int = 3
    period: int = 300  # 5 minutes
    statistics: str = "Average"  # Average, Maximum, Minimum
    actions: List[str] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []

@dataclass
class Dashboard:
    """Dashboard configuration"""
    dashboard_name: str
    charts: List[Dict[str, Any]]

class MonitoringConfigGenerator:
    """Generate comprehensive monitoring configuration"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_name = "bailian-demo"
    
    def create_alert_rules(self) -> List[AlertRule]:
        """Create comprehensive alert rules"""
        return [
            # Application health alerts
            AlertRule(
                rule_name=f"{self.project_name}-high-error-rate",
                metric_name="http_errors_rate",
                namespace="acs_ecs_dashboard",
                dimensions={"instanceId": "i-*"},
                comparison_operator="GreaterThanThreshold",
                threshold=5.0,  # 5% error rate
                actions=["arn:acs:ess:*:*:scalinggroup/high-priority-alert"]
            ),
            
            # Resource utilization alerts
            AlertRule(
                rule_name=f"{self.project_name}-high-cpu",
                metric_name="CPUUtilization",
                namespace="acs_ecs_dashboard",
                dimensions={"instanceId": "i-*"},
                comparison_operator="GreaterThanThreshold",
                threshold=80.0,
                statistics="Average"
            ),
            
            AlertRule(
                rule_name=f"{self.project_name}-high-memory",
                metric_name="MemoryUtilization",
                namespace="acs_ecs_dashboard", 
                dimensions={"instanceId": "i-*"},
                comparison_operator="GreaterThanThreshold",
                threshold=85.0
            ),
            
            # Database alerts
            AlertRule(
                rule_name=f"{self.project_name}-db-connections",
                metric_name="ConnectionUsage",
                namespace="acs_rds_dashboard",
                dimensions={"instanceId": "rm-*"},
                comparison_operator="GreaterThanThreshold",
                threshold=80.0
            ),
            
            # AI service alerts
            AlertRule(
                rule_name=f"{self.project_name}-ai-latency",
                metric_name="ai_request_duration",
                namespace="acs_customMetric",
                dimensions={"service": "bailian"},
                comparison_operator="GreaterThanThreshold",
                threshold=5000.0,  # 5 seconds
                statistics="Average"
            ),
        ]
    
    def create_dashboard_config(self) -> Dashboard:
        """Create monitoring dashboard"""
        charts = [
            {
                "type": "line",
                "title": "API Response Time",
                "metrics": [
                    {
                        "namespace": "acs_customMetric",
                        "metricName": "http_request_duration",
                        "dimensions": {"service": "backend"}
                    }
                ]
            },
            {
                "type": "line", 
                "title": "Request Rate",
                "metrics": [
                    {
                        "namespace": "acs_customMetric",
                        "metricName": "http_requests_total",
                        "dimensions": {"service": "backend"}
                    }
                ]
            },
            {
                "type": "line",
                "title": "Error Rate",
                "metrics": [
                    {
                        "namespace": "acs_customMetric", 
                        "metricName": "http_errors_total",
                        "dimensions": {"service": "backend"}
                    }
                ]
            },
            {
                "type": "gauge",
                "title": "System Resources",
                "metrics": [
                    {
                        "namespace": "acs_ecs_dashboard",
                        "metricName": "CPUUtilization"
                    },
                    {
                        "namespace": "acs_ecs_dashboard",
                        "metricName": "MemoryUtilization"
                    }
                ]
            }
        ]
        
        return Dashboard(
            dashboard_name=f"{self.project_name}-monitoring-{self.environment}",
            charts=charts
        )
    
    def generate_terraform_config(self) -> str:
        """Generate Terraform configuration for monitoring"""
        alert_rules = self.create_alert_rules()
        dashboard = self.create_dashboard_config()
        
        config = f"""
# CloudMonitor Configuration for {self.project_name}

resource "alicloud_cms_alarm_contact_group" "main" {{
  alarm_contact_group_name = "{self.project_name}-alerts-{self.environment}"
  describe                 = "Alert contact group for {self.project_name}"
  contacts                 = ["admin@example.com"]
}}

# Alert Rules
"""
        
        for rule in alert_rules:
            rule_name_tf = rule.rule_name.replace("-", "_")
            config += f"""
resource "alicloud_cms_alarm" "{rule_name_tf}" {{
  name         = "{rule.rule_name}"
  project      = "{rule.namespace}"
  metric       = "{rule.metric_name}"
  dimensions   = {json.dumps(rule.dimensions)}
  statistics   = "{rule.statistics}"
  period       = {rule.period}
  operator     = "{rule.comparison_operator}"
  threshold    = "{rule.threshold}"
  triggered_count = {rule.evaluation_periods}
  contact_groups = [alicloud_cms_alarm_contact_group.main.id]
  enabled      = true
}}
"""
        
        # Dashboard configuration
        config += f"""
# Dashboard
resource "alicloud_cms_group_metric_rule" "dashboard_rules" {{
  group_id    = alicloud_cms_monitor_group.main.id
  rule_name   = "{dashboard.dashboard_name}"
  category    = "ecs"
  metric_name = "CPUUtilization"
  namespace   = "acs_ecs_dashboard"
  
  escalations_critical {{
    comparison_operator = "GreaterThanThreshold"
    statistics         = "Average"
    threshold          = "90"
    times              = 3
  }}
}}

resource "alicloud_cms_monitor_group" "main" {{
  monitor_group_name = "{self.project_name}-group-{self.environment}"
  contact_groups     = [alicloud_cms_alarm_contact_group.main.alarm_contact_group_name]
}}
"""
        
        return config

def main():
    """Generate monitoring configuration"""
    generator = MonitoringConfigGenerator("production")
    terraform_config = generator.generate_terraform_config()
    
    with open("monitoring_terraform.tf", "w") as f:
        f.write(terraform_config)
    
    print("✅ Monitoring configuration generated: monitoring_terraform.tf")

if __name__ == "__main__":
    main()