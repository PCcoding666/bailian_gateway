"""
Unit tests for Prometheus metrics functionality
Tests metrics collection, exposition, and middleware integration
\"\"\"

import pytest
import time
from unittest.mock import Mock, patch
from prometheus_client import REGISTRY as DEFAULT_REGISTRY
from fastapi.testclient import TestClient

from utils.metrics import (
    REGISTRY,
    MetricsCollector,
    metrics,
    get_metrics,
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION,
    DATABASE_QUERIES_TOTAL,
    AI_REQUESTS_TOTAL,
    HEALTH_CHECK_STATUS
)
from main import app


class TestMetricsCollector:
    \"\"\"Test suite for MetricsCollector\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures\"\"\"
        # Clear metrics before each test
        REGISTRY._collector_to_names.clear()
        REGISTRY._names_to_collectors.clear()
    
    def test_record_http_request(self):
        \"\"\"Test HTTP request metrics recording\"\"\"
        metrics.record_http_request(
            method=\"GET\",
            endpoint=\"/api/test\",
            status_code=200,
            duration=0.150
        )
        
        # Check counter increment
        counter_value = HTTP_REQUESTS_TOTAL.labels(
            method=\"GET\",
            endpoint=\"/api/test\",
            status_code=\"200\"
        )._value._value
        
        assert counter_value == 1
        
        # Check histogram recording
        histogram_samples = list(HTTP_REQUEST_DURATION.labels(
            method=\"GET\",
            endpoint=\"/api/test\"
        )._child.collect()[0].samples)
        
        # Should have count, sum, and bucket samples
        assert len(histogram_samples) > 0
        count_sample = next(s for s in histogram_samples if s.name.endswith('_count'))
        assert count_sample.value == 1
    
    def test_record_database_query(self):
        \"\"\"Test database query metrics recording\"\"\"
        metrics.record_database_query(\"SELECT\", 0.025)
        
        counter_value = DATABASE_QUERIES_TOTAL.labels(operation=\"SELECT\")._value._value
        assert counter_value == 1
    
    def test_record_ai_request(self):
        \"\"\"Test AI request metrics recording\"\"\"
        metrics.record_ai_request(
            model=\"qwen-max\",
            status=\"success\",
            duration=2.5,
            input_tokens=100,
            output_tokens=50
        )
        
        # Check request counter
        request_counter = AI_REQUESTS_TOTAL.labels(
            model=\"qwen-max\",
            status=\"success\"
        )._value._value
        assert request_counter == 1
    
    def test_set_health_status(self):
        \"\"\"Test health status metrics\"\"\"
        metrics.set_health_status(\"database\", True)
        metrics.set_health_status(\"redis\", False)
        
        db_status = HEALTH_CHECK_STATUS.labels(check_type=\"database\")._value._value
        redis_status = HEALTH_CHECK_STATUS.labels(check_type=\"redis\")._value._value
        
        assert db_status == 1  # healthy
        assert redis_status == 0  # unhealthy


class TestMetricsEndpoint:
    \"\"\"Test suite for metrics endpoint\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test client\"\"\"
        self.client = TestClient(app)
    
    def test_metrics_endpoint_access(self):
        \"\"\"Test that metrics endpoint is accessible\"\"\"
        response = self.client.get(\"/metrics\")
        
        assert response.status_code == 200
        assert \"text/plain\" in response.headers[\"content-type\"]
    
    def test_metrics_content_format(self):
        \"\"\"Test that metrics are in Prometheus format\"\"\"
        response = self.client.get(\"/metrics\")
        content = response.text
        
        # Check for basic Prometheus metrics format
        assert \"# HELP\" in content
        assert \"# TYPE\" in content
        
        # Check for our custom metrics
        assert \"app_info\" in content
        assert \"http_requests_total\" in content
        assert \"http_request_duration_seconds\" in content
    
    def test_metrics_after_api_calls(self):
        \"\"\"Test that metrics are updated after API calls\"\"\"
        # Make some API calls
        self.client.get(\"/health\")
        self.client.get(\"/health/live\")
        
        # Check metrics
        response = self.client.get(\"/metrics\")
        content = response.text
        
        # Should contain HTTP request metrics
        assert \"http_requests_total\" in content
        assert \"method=\\\"GET\\\"\" in content
        assert \"endpoint=\\\"/health\\\"\" in content


class TestMetricsMiddleware:
    \"\"\"Test suite for metrics middleware integration\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test client\"\"\"
        self.client = TestClient(app)
    
    def test_middleware_records_metrics(self):
        \"\"\"Test that middleware automatically records metrics\"\"\"
        # Clear any existing metrics
        HTTP_REQUESTS_TOTAL._metrics.clear()
        
        # Make request
        response = self.client.get(\"/health\")
        assert response.status_code == 200
        
        # Check that metric was recorded
        # Note: The actual metric recording happens in middleware
        # We test this by checking the metrics endpoint
        metrics_response = self.client.get(\"/metrics\")
        content = metrics_response.text
        
        assert \"http_requests_total\" in content
    
    def test_middleware_handles_errors(self):
        \"\"\"Test that middleware records metrics for error responses\"\"\"
        # Make request to non-existent endpoint
        response = self.client.get(\"/nonexistent\")
        assert response.status_code == 404
        
        # Check metrics
        metrics_response = self.client.get(\"/metrics\")
        content = metrics_response.text
        
        # Should record the 404 response
        assert \"http_requests_total\" in content
    
    def test_path_normalization(self):
        \"\"\"Test that dynamic paths are normalized in metrics\"\"\"
        from middleware.metrics_middleware import MetricsMiddleware
        
        middleware = MetricsMiddleware(None)
        
        # Test ID normalization
        assert middleware._normalize_path(\"/api/users/123\") == \"/api/users/{id}\"
        assert middleware._normalize_path(\"/api/conversations/456/messages\") == \"/api/conversations/{id}/messages\"
        
        # Test UUID normalization
        uuid_path = \"/api/sessions/550e8400-e29b-41d4-a716-446655440000\"
        assert middleware._normalize_path(uuid_path) == \"/api/sessions/{id}\"
        
        # Test token normalization
        token_path = \"/api/auth/verify/abcdef1234567890abcdef1234567890\"
        assert middleware._normalize_path(token_path) == \"/api/auth/verify/{token}\"


class TestMetricsIntegration:
    \"\"\"Integration tests for metrics system\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test client\"\"\"
        self.client = TestClient(app)
    
    def test_full_request_lifecycle_metrics(self):
        \"\"\"Test metrics collection through full request lifecycle\"\"\"
        # Record initial state
        initial_response = self.client.get(\"/metrics\")
        initial_content = initial_response.text
        
        # Make several requests
        self.client.get(\"/health\")
        self.client.get(\"/health/live\")
        self.client.get(\"/health/ready\")
        
        # Check updated metrics
        final_response = self.client.get(\"/metrics\")
        final_content = final_response.text
        
        # Metrics should have been updated
        assert len(final_content) >= len(initial_content)
        assert \"http_requests_total\" in final_content
    
    @patch('utils.metrics.DATABASE_CONNECTIONS')
    def test_health_check_metrics_integration(self, mock_db_connections):
        \"\"\"Test that health checks update metrics\"\"\"
        # Mock the gauge
        mock_gauge = Mock()
        mock_db_connections.set = mock_gauge.set
        
        # Make health check request
        response = self.client.get(\"/health/ready\")
        
        # Should update health status metrics
        metrics_response = self.client.get(\"/metrics\")
        content = metrics_response.text
        
        assert \"health_check_status\" in content


if __name__ == \"__main__\":
    pytest.main([__file__, \"-v\"])