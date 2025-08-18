"""
Cloud Configuration Management for Alibaba Cloud Integration
Supports Parameter Store, environment variables, and Kubernetes ConfigMaps/Secrets
"""

import os
import json
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from pathlib import Path
from functools import lru_cache
import boto3
from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_tea_openapi import models as open_api_models
from utils.cloud_logger import cloud_logger

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 3306
    database: str = "bailian"
    username: str = "root"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    ssl_disabled: bool = True

@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    database: int = 0
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    health_check_interval: int = 30

@dataclass
class AIServiceConfig:
    """AI service configuration"""
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    qwen_model: str = "qwen-max"
    wanx_model: str = "wanx-v1"
    timeout: int = 30
    max_retries: int = 3
    rate_limit_per_minute: int = 100

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 7
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_headers: List[str] = field(default_factory=lambda: ["*"])

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"
    correlation_id_header: str = "X-Correlation-ID"
    log_sql_queries: bool = False
    log_request_body: bool = False
    log_response_body: bool = False

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    metrics_enabled: bool = True
    metrics_path: str = "/metrics"
    health_check_enabled: bool = True
    prometheus_multiproc: bool = False
    custom_metrics_enabled: bool = True

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    enabled: bool = True
    default_requests_per_minute: int = 100
    burst_size: int = 200
    admin_requests_per_minute: int = 1000
    premium_requests_per_minute: int = 500
    window_size_seconds: int = 60

@dataclass
class ApplicationConfig:
    """Main application configuration"""
    app_name: str = "bailian-backend"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    ai_service: AIServiceConfig = field(default_factory=AIServiceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

class ConfigurationManager:
    """Centralized configuration management for cloud environments"""
    
    def __init__(self, config_sources: Optional[List[str]] = None):
        """
        Initialize configuration manager
        
        Args:
            config_sources: Priority-ordered list of config sources
                          ['env', 'parameter_store', 'k8s_secrets', 'file']
        """
        self.config_sources = config_sources or ['env', 'parameter_store', 'k8s_secrets', 'file']
        self._config_cache: Dict[str, Any] = {}
        self._parameter_store_client = None
        
    def load_configuration(self) -> ApplicationConfig:
        """Load configuration from all sources with priority order"""
        config_data = {}
        
        for source in self.config_sources:
            try:
                source_data = self._load_from_source(source)
                # Merge with lower priority (later sources override earlier ones)
                config_data = self._deep_merge(config_data, source_data)
                cloud_logger.info(f"Loaded configuration from {source}", source=source)
            except Exception as e:
                cloud_logger.warning(f"Failed to load configuration from {source}: {str(e)}", 
                                   source=source, error=str(e))
        
        # Create configuration objects
        return self._create_config_objects(config_data)
    
    def _load_from_source(self, source: str) -> Dict[str, Any]:
        """Load configuration from specific source"""
        if source == 'env':
            return self._load_from_environment()
        elif source == 'parameter_store':
            return self._load_from_parameter_store()
        elif source == 'k8s_secrets':
            return self._load_from_k8s_secrets()
        elif source == 'file':
            return self._load_from_file()
        else:
            cloud_logger.warning(f"Unknown configuration source: {source}")
            return {}
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        
        # Application settings
        config['app_name'] = os.getenv('APP_NAME', 'bailian-backend')
        config['app_version'] = os.getenv('APP_VERSION', '1.0.0')
        config['environment'] = os.getenv('APP_ENV', 'development')
        config['debug'] = os.getenv('DEBUG', 'false').lower() == 'true'
        config['host'] = os.getenv('HOST', '0.0.0.0')
        config['port'] = int(os.getenv('PORT', '8000'))
        config['workers'] = int(os.getenv('WORKERS', '1'))
        
        # Database configuration
        config['database'] = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'database': os.getenv('DB_NAME', 'bailian'),
            'username': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
            'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
            'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
            'ssl_disabled': os.getenv('DB_SSL_DISABLED', 'true').lower() == 'true'
        }
        
        # Redis configuration
        config['redis'] = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'password': os.getenv('REDIS_PASSWORD'),
            'database': int(os.getenv('REDIS_DATABASE', '0')),
            'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', '10')),
            'socket_timeout': int(os.getenv('REDIS_SOCKET_TIMEOUT', '5')),
            'socket_connect_timeout': int(os.getenv('REDIS_CONNECT_TIMEOUT', '5')),
            'health_check_interval': int(os.getenv('REDIS_HEALTH_CHECK_INTERVAL', '30'))
        }
        
        # AI Service configuration
        config['ai_service'] = {
            'dashscope_api_key': os.getenv('QWEN_API_KEY', ''),
            'dashscope_base_url': os.getenv('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/api/v1'),
            'qwen_model': os.getenv('QWEN_MODEL', 'qwen-max'),
            'wanx_model': os.getenv('WANX_MODEL', 'wanx-v1'),
            'timeout': int(os.getenv('AI_SERVICE_TIMEOUT', '30')),
            'max_retries': int(os.getenv('AI_SERVICE_MAX_RETRIES', '3')),
            'rate_limit_per_minute': int(os.getenv('AI_SERVICE_RATE_LIMIT', '100'))
        }
        
        # Security configuration
        config['security'] = {
            'jwt_secret_key': os.getenv('JWT_SECRET_KEY', ''),
            'jwt_algorithm': os.getenv('JWT_ALGORITHM', 'HS256'),
            'jwt_expiration_hours': int(os.getenv('JWT_EXPIRATION_HOURS', '24')),
            'jwt_refresh_expiration_days': int(os.getenv('JWT_REFRESH_EXPIRATION_DAYS', '7')),
            'cors_origins': os.getenv('CORS_ORIGINS', '*').split(','),
            'cors_allow_credentials': os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true',
            'cors_allow_methods': os.getenv('CORS_ALLOW_METHODS', '*').split(','),
            'cors_allow_headers': os.getenv('CORS_ALLOW_HEADERS', '*').split(',')
        }
        
        # Logging configuration
        config['logging'] = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': os.getenv('LOG_FORMAT', 'json'),
            'correlation_id_header': os.getenv('CORRELATION_ID_HEADER', 'X-Correlation-ID'),
            'log_sql_queries': os.getenv('LOG_SQL_QUERIES', 'false').lower() == 'true',
            'log_request_body': os.getenv('LOG_REQUEST_BODY', 'false').lower() == 'true',
            'log_response_body': os.getenv('LOG_RESPONSE_BODY', 'false').lower() == 'true'
        }
        
        # Monitoring configuration
        config['monitoring'] = {
            'metrics_enabled': os.getenv('METRICS_ENABLED', 'true').lower() == 'true',
            'metrics_path': os.getenv('METRICS_PATH', '/metrics'),
            'health_check_enabled': os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true',
            'prometheus_multiproc': os.getenv('PROMETHEUS_MULTIPROC', 'false').lower() == 'true',
            'custom_metrics_enabled': os.getenv('CUSTOM_METRICS_ENABLED', 'true').lower() == 'true'
        }
        
        # Rate limiting configuration
        config['rate_limit'] = {
            'enabled': os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true',
            'default_requests_per_minute': int(os.getenv('RATE_LIMIT_DEFAULT', '100')),
            'burst_size': int(os.getenv('RATE_LIMIT_BURST', '200')),
            'admin_requests_per_minute': int(os.getenv('RATE_LIMIT_ADMIN', '1000')),
            'premium_requests_per_minute': int(os.getenv('RATE_LIMIT_PREMIUM', '500')),
            'window_size_seconds': int(os.getenv('RATE_LIMIT_WINDOW', '60'))
        }
        
        return config
    
    def _load_from_parameter_store(self) -> Dict[str, Any]:
        """Load configuration from Alibaba Cloud Parameter Store"""
        try:
            # This would integrate with Alibaba Cloud OOS Parameter Store
            # For now, return empty dict as the actual implementation requires
            # Alibaba Cloud SDK setup
            cloud_logger.info("Parameter Store integration not yet implemented")
            return {}
        except Exception as e:
            cloud_logger.error(f"Failed to load from Parameter Store: {str(e)}")
            return {}
    
    def _load_from_k8s_secrets(self) -> Dict[str, Any]:
        """Load configuration from Kubernetes secrets and configmaps"""
        config = {}
        
        # Check for mounted secret files
        secret_paths = [
            '/app/secrets/',
            '/var/secrets/',
            '/etc/secrets/'
        ]
        
        for secret_path in secret_paths:
            if os.path.exists(secret_path):
                try:
                    for file_name in os.listdir(secret_path):
                        file_path = os.path.join(secret_path, file_name)
                        if os.path.isfile(file_path):
                            with open(file_path, 'r') as f:
                                config[file_name] = f.read().strip()
                except Exception as e:
                    cloud_logger.warning(f"Failed to read secret from {secret_path}: {str(e)}")
        
        return config
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from configuration files"""
        config_files = [
            'config/app.json',
            'config/app.yaml',
            '/app/config/app.json',
            '/etc/bailian/config.json'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        if config_file.endswith('.json'):
                            return json.load(f)
                        elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                            import yaml
                            return yaml.safe_load(f)
                except Exception as e:
                    cloud_logger.warning(f"Failed to load config file {config_file}: {str(e)}")
        
        return {}
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_config_objects(self, config_data: Dict[str, Any]) -> ApplicationConfig:
        """Create strongly-typed configuration objects"""
        # Database config
        db_config = DatabaseConfig(**config_data.get('database', {}))
        
        # Redis config
        redis_config = RedisConfig(**config_data.get('redis', {}))
        
        # AI Service config
        ai_config = AIServiceConfig(**config_data.get('ai_service', {}))
        
        # Security config
        security_config = SecurityConfig(**config_data.get('security', {}))
        
        # Logging config
        logging_config = LoggingConfig(**config_data.get('logging', {}))
        
        # Monitoring config
        monitoring_config = MonitoringConfig(**config_data.get('monitoring', {}))
        
        # Rate limit config
        rate_limit_config = RateLimitConfig(**config_data.get('rate_limit', {}))
        
        # Main app config
        app_config = ApplicationConfig(
            app_name=config_data.get('app_name', 'bailian-backend'),
            app_version=config_data.get('app_version', '1.0.0'),
            environment=config_data.get('environment', 'development'),
            debug=config_data.get('debug', False),
            host=config_data.get('host', '0.0.0.0'),
            port=config_data.get('port', 8000),
            workers=config_data.get('workers', 1),
            database=db_config,
            redis=redis_config,
            ai_service=ai_config,
            security=security_config,
            logging=logging_config,
            monitoring=monitoring_config,
            rate_limit=rate_limit_config
        )
        
        return app_config

# Global configuration manager instance
config_manager = ConfigurationManager()

@lru_cache(maxsize=1)
def get_config() -> ApplicationConfig:
    """Get application configuration (cached)"""
    return config_manager.load_configuration()

def reload_config() -> ApplicationConfig:
    """Reload configuration (clears cache)"""
    get_config.cache_clear()
    return get_config()

# Convenience functions for accessing specific config sections
def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return get_config().database

def get_redis_config() -> RedisConfig:
    """Get Redis configuration"""
    return get_config().redis

def get_ai_service_config() -> AIServiceConfig:
    """Get AI service configuration"""
    return get_config().ai_service

def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    return get_config().security

def get_logging_config() -> LoggingConfig:
    """Get logging configuration"""
    return get_config().logging

def get_monitoring_config() -> MonitoringConfig:
    """Get monitoring configuration"""
    return get_config().monitoring

def get_rate_limit_config() -> RateLimitConfig:
    """Get rate limiting configuration"""
    return get_config().rate_limit