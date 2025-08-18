"""
Unit tests for cloud logging functionality
Tests JSON logging, correlation IDs, and structured logging features
\"\"\"

import pytest
import json
import logging
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from contextvars import copy_context

from utils.cloud_logger import (
    CloudLogger,
    CloudJSONFormatter,
    correlation_id,
    generate_correlation_id,
    set_correlation_id,
    get_correlation_id,
    log_execution_time
)


class TestCloudJSONFormatter:
    \"\"\"Test suite for CloudJSONFormatter\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures\"\"\"
        self.formatter = CloudJSONFormatter()
        self.log_record = logging.LogRecord(
            name=\"test_logger\",
            level=logging.INFO,
            pathname=\"/app/test.py\",
            lineno=42,
            msg=\"Test message\",
            args=(),
            exc_info=None
        )
    
    def test_format_basic_log(self):
        \"\"\"Test basic log formatting\"\"\"
        formatted = self.formatter.format(self.log_record)
        data = json.loads(formatted)
        
        assert data[\"level\"] == \"INFO\"
        assert data[\"logger\"] == \"test_logger\"
        assert data[\"message\"] == \"Test message\"
        assert data[\"service\"] == \"bailian-backend\"
        assert data[\"version\"] == \"0.1.0\"
        assert \"timestamp\" in data
        assert \"correlation_id\" in data
        assert \"thread\" in data
        assert \"module\" in data
        assert \"function\" in data
        assert \"line\" in data
    
    def test_format_with_correlation_id(self):
        \"\"\"Test log formatting with correlation ID\"\"\"
        test_correlation_id = \"test-123-456\"
        set_correlation_id(test_correlation_id)
        
        formatted = self.formatter.format(self.log_record)
        data = json.loads(formatted)
        
        assert data[\"correlation_id\"] == test_correlation_id
    
    def test_format_with_exception(self):
        \"\"\"Test log formatting with exception info\"\"\"
        try:
            raise ValueError(\"Test exception\")
        except ValueError:
            import sys
            self.log_record.exc_info = sys.exc_info()
        
        formatted = self.formatter.format(self.log_record)
        data = json.loads(formatted)
        
        assert \"exception\" in data
        assert data[\"exception\"][\"type\"] == \"ValueError\"
        assert data[\"exception\"][\"message\"] == \"Test exception\"
        assert \"traceback\" in data[\"exception\"]
    
    def test_format_with_extra_fields(self):
        \"\"\"Test log formatting with extra fields\"\"\"
        self.log_record.extra_fields = {
            \"user_id\": 123,
            \"action\": \"test_action\",
            \"duration_ms\": 250.5
        }
        
        formatted = self.formatter.format(self.log_record)
        data = json.loads(formatted)
        
        assert data[\"user_id\"] == 123
        assert data[\"action\"] == \"test_action\"
        assert data[\"duration_ms\"] == 250.5


class TestCloudLogger:
    \"\"\"Test suite for CloudLogger\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures\"\"\"
        self.logger = CloudLogger(\"test_logger\")
        
        # Capture log output
        self.log_output = StringIO()
        handler = logging.StreamHandler(self.log_output)
        handler.setFormatter(CloudJSONFormatter())
        
        # Replace handler
        self.logger.logger.handlers.clear()
        self.logger.logger.addHandler(handler)
        self.logger.logger.setLevel(logging.DEBUG)
    
    def test_debug_logging(self):
        \"\"\"Test debug level logging\"\"\"
        self.logger.debug(\"Debug message\", user_id=123)
        
        log_output = self.log_output.getvalue()
        data = json.loads(log_output.strip())
        
        assert data[\"level\"] == \"DEBUG\"
        assert data[\"message\"] == \"Debug message\"
        assert data[\"user_id\"] == 123
    
    def test_info_logging(self):
        \"\"\"Test info level logging\"\"\"
        self.logger.info(\"Info message\", action=\"test\")
        
        log_output = self.log_output.getvalue()
        data = json.loads(log_output.strip())
        
        assert data[\"level\"] == \"INFO\"
        assert data[\"message\"] == \"Info message\"
        assert data[\"action\"] == \"test\"
    
    def test_error_logging(self):
        \"\"\"Test error level logging\"\"\"
        self.logger.error(\"Error message\", error_code=\"TEST_ERROR\")
        
        log_output = self.log_output.getvalue()
        data = json.loads(log_output.strip())
        
        assert data[\"level\"] == \"ERROR\"
        assert data[\"message\"] == \"Error message\"
        assert data[\"error_code\"] == \"TEST_ERROR\"
    
    def test_api_call_logging(self):
        \"\"\"Test API call structured logging\"\"\"
        self.logger.api_call(
            method=\"POST\",
            endpoint=\"/api/test\",
            status_code=200,
            duration_ms=150.5,
            user_id=123
        )
        
        log_output = self.log_output.getvalue()
        data = json.loads(log_output.strip())
        
        assert data[\"event_type\"] == \"api_call\"
        assert data[\"http_method\"] == \"POST\"
        assert data[\"endpoint\"] == \"/api/test\"
        assert data[\"status_code\"] == 200
        assert data[\"duration_ms\"] == 150.5
        assert data[\"user_id\"] == 123
    
    def test_business_event_logging(self):
        \"\"\"Test business event structured logging\"\"\"
        self.logger.business_event(
            \"user_registration\",
            user_id=123,
            email=\"test@example.com\"
        )
        
        log_output = self.log_output.getvalue()
        data = json.loads(log_output.strip())
        
        assert data[\"event_type\"] == \"business_event\"
        assert data[\"event_name\"] == \"user_registration\"
        assert data[\"user_id\"] == 123
        assert data[\"email\"] == \"test@example.com\"
    
    def test_security_event_logging(self):
        \"\"\"Test security event structured logging\"\"\"
        self.logger.security_event(
            \"failed_login_attempt\",
            \"HIGH\",
            user_id=123,
            ip_address=\"192.168.1.1\"
        )
        
        log_output = self.log_output.getvalue()
        data = json.loads(log_output.strip())
        
        assert data[\"level\"] == \"ERROR\"  # HIGH severity -> ERROR level
        assert data[\"event_type\"] == \"security_event\"
        assert data[\"security_event_type\"] == \"failed_login_attempt\"
        assert data[\"severity\"] == \"HIGH\"
        assert data[\"user_id\"] == 123
        assert data[\"ip_address\"] == \"192.168.1.1\"


class TestCorrelationID:
    \"\"\"Test suite for correlation ID functionality\"\"\"
    
    def test_generate_correlation_id(self):
        \"\"\"Test correlation ID generation\"\"\"
        corr_id = generate_correlation_id()
        
        assert isinstance(corr_id, str)
        assert len(corr_id) > 0
        assert \"-\" in corr_id  # UUID format
    
    def test_set_get_correlation_id(self):
        \"\"\"Test setting and getting correlation ID\"\"\"
        test_id = \"test-correlation-123\"
        
        set_correlation_id(test_id)
        retrieved_id = get_correlation_id()
        
        assert retrieved_id == test_id
    
    def test_correlation_id_context_isolation(self):
        \"\"\"Test correlation ID context isolation\"\"\"
        # Set in main context
        set_correlation_id(\"main-context\")
        
        # Create new context
        ctx = copy_context()
        
        def set_in_context():
            set_correlation_id(\"new-context\")
            return get_correlation_id()
        
        # Run in new context
        new_context_id = ctx.run(set_in_context)
        
        # Check isolation
        assert get_correlation_id() == \"main-context\"
        assert new_context_id == \"new-context\"


class TestLogExecutionTimeDecorator:
    \"\"\"Test suite for log execution time decorator\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test fixtures\"\"\"
        self.logger = CloudLogger(\"test_logger\")
        
        # Capture log output
        self.log_output = StringIO()
        handler = logging.StreamHandler(self.log_output)
        handler.setFormatter(CloudJSONFormatter())
        
        # Replace handler 
        self.logger.logger.handlers.clear()
        self.logger.logger.addHandler(handler)
        self.logger.logger.setLevel(logging.DEBUG)
    
    def test_successful_execution_logging(self):
        \"\"\"Test logging of successful function execution\"\"\"
        @log_execution_time(self.logger)
        def test_function(x, y):
            return x + y
        
        result = test_function(2, 3)
        
        assert result == 5
        
        log_output = self.log_output.getvalue()
        data = json.loads(log_output.strip())
        
        assert data[\"level\"] == \"DEBUG\"
        assert \"test_function executed successfully\" in data[\"message\"]
        assert data[\"function\"] == \"test_function\"
        assert data[\"status\"] == \"success\"
        assert \"duration_ms\" in data
        assert data[\"duration_ms\"] >= 0
    
    def test_failed_execution_logging(self):
        \"\"\"Test logging of failed function execution\"\"\"
        @log_execution_time(self.logger)
        def failing_function():
            raise ValueError(\"Test error\")
        
        with pytest.raises(ValueError):
            failing_function()
        
        log_output = self.log_output.getvalue()
        data = json.loads(log_output.strip())
        
        assert data[\"level\"] == \"ERROR\"
        assert \"failing_function failed with error\" in data[\"message\"]
        assert data[\"function\"] == \"failing_function\"
        assert data[\"status\"] == \"error\"
        assert data[\"error_type\"] == \"ValueError\"
        assert data[\"error_message\"] == \"Test error\"
        assert \"duration_ms\" in data


if __name__ == \"__main__\":
    pytest.main([__file__, \"-v\"])