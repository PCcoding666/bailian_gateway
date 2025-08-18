"""
Unit tests for health check endpoints
Tests liveness, readiness, and basic health checks for Kubernetes deployment
\"\"\"

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError

# Import the main app and dependencies
from main import app
from config.database import get_db


class TestHealthChecks:
    \"\"\"Test suite for health check endpoints\"\"\"
    
    def setup_method(self):
        \"\"\"Set up test client and mocks\"\"\"
        self.client = TestClient(app)
    
    def test_basic_health_check(self):
        \"\"\"Test basic health check endpoint\"\"\"
        response = self.client.get(\"/health\")
        
        assert response.status_code == 200
        data = response.json()
        assert data[\"status\"] == \"healthy\"
        assert \"timestamp\" in data
    
    def test_liveness_probe(self):
        \"\"\"Test Kubernetes liveness probe endpoint\"\"\"
        response = self.client.get(\"/health/live\")
        
        assert response.status_code == 200
        data = response.json()
        assert data[\"status\"] == \"alive\"
        assert data[\"service\"] == \"bailian-backend\"
        assert data[\"version\"] == \"0.1.0\"
        assert \"timestamp\" in data
    
    @patch('main.get_db')
    @patch('main.redis.Redis')
    @patch('main.os.getenv')
    def test_readiness_probe_healthy(self, mock_getenv, mock_redis, mock_get_db):
        \"\"\"Test readiness probe when all services are healthy\"\"\"
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock Redis
        mock_redis_client = Mock()
        mock_redis_client.ping.return_value = True
        mock_redis.return_value = mock_redis_client
        
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': '6379',
            'QWEN_API_KEY': 'test-api-key'
        }.get(key, default)
        
        response = self.client.get(\"/health/ready\")
        
        assert response.status_code == 200
        data = response.json()
        assert data[\"status\"] == \"ready\"
        assert data[\"checks\"][\"database\"] == \"connected\"
        assert data[\"checks\"][\"redis\"] == \"connected\"
        assert data[\"checks\"][\"dashscope_api\"] == \"configured\"
    
    @patch('main.get_db')
    def test_readiness_probe_database_error(self, mock_get_db):
        \"\"\"Test readiness probe when database is unavailable\"\"\"
        # Mock database session that raises exception
        mock_db = Mock()
        mock_db.execute.side_effect = SQLAlchemyError(\"Database connection failed\")
        mock_get_db.return_value = mock_db
        
        response = self.client.get(\"/health/ready\")
        
        assert response.status_code == 503
        data = response.json()
        assert \"error\" in data
        assert \"checks\" in data[\"detail\"]
        assert \"database\" in data[\"detail\"][\"checks\"]
        assert \"error\" in data[\"detail\"][\"checks\"][\"database\"]
    
    @patch('main.get_db')
    @patch('main.redis.Redis')
    @patch('main.os.getenv')
    def test_readiness_probe_redis_error(self, mock_getenv, mock_redis, mock_get_db):
        \"\"\"Test readiness probe when Redis is unavailable\"\"\"
        # Mock database session (healthy)
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock Redis that raises exception
        mock_redis_client = Mock()
        mock_redis_client.ping.side_effect = RedisError(\"Redis connection failed\")
        mock_redis.return_value = mock_redis_client
        
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': '6379',
            'QWEN_API_KEY': 'test-api-key'
        }.get(key, default)
        
        response = self.client.get(\"/health/ready\")
        
        assert response.status_code == 503
        data = response.json()
        assert \"error\" in data
        assert \"checks\" in data[\"detail\"]
        assert \"redis\" in data[\"detail\"][\"checks\"]
        assert \"error\" in data[\"detail\"][\"checks\"][\"redis\"]
    
    @patch('main.get_db')
    @patch('main.redis.Redis')
    @patch('main.os.getenv')
    def test_readiness_probe_missing_api_key(self, mock_getenv, mock_redis, mock_get_db):
        \"\"\"Test readiness probe when API key is not configured\"\"\"
        # Mock database session (healthy)
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock Redis (healthy)
        mock_redis_client = Mock()
        mock_redis_client.ping.return_value = True
        mock_redis.return_value = mock_redis_client
        
        # Mock environment variables without API key
        mock_getenv.side_effect = lambda key, default=None: {
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': '6379',
            'QWEN_API_KEY': None
        }.get(key, default)
        
        response = self.client.get(\"/health/ready\")
        
        assert response.status_code == 503
        data = response.json()
        assert \"error\" in data
        assert \"checks\" in data[\"detail\"]
        assert data[\"detail\"][\"checks\"][\"dashscope_api\"] == \"not_configured\"
    
    def test_root_endpoint(self):
        \"\"\"Test root endpoint returns service information\"\"\"
        response = self.client.get(\"/\")
        
        assert response.status_code == 200
        data = response.json()
        assert data[\"service\"] == \"bailian-backend\"
        assert data[\"version\"] == \"0.1.0\"
        assert \"message\" in data
        assert \"docs\" in data
        assert \"health\" in data
        assert \"ready\" in data
        assert \"alive\" in data
    
    def test_metrics_endpoint(self):
        \"\"\"Test Prometheus metrics endpoint\"\"\"
        response = self.client.get(\"/metrics\")
        
        assert response.status_code == 200
        assert \"text/plain\" in response.headers[\"content-type\"]
        # Check for some basic metrics
        content = response.text
        assert \"app_info\" in content
        assert \"http_requests_total\" in content


if __name__ == \"__main__\":
    pytest.main([__file__, \"-v\"])