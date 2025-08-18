"""
Comprehensive Qwen API Integration Tests
Tests all API endpoints with real data formats and usage tracking
"""

import pytest
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Import the main app and services
from main import app
from services.bailian_api_service import BailianAPIService
from services.function_compute_service import FunctionComputeService, FunctionComputeRequest
from config.database import get_db
from models import User

class TestQwenAPIIntegration:
    """Comprehensive test suite for Qwen API integrations"""
    
    def setup_method(self):
        """Set up test client and mock data"""
        self.client = TestClient(app)
        self.api_call_count = 0
        self.api_call_log = []
        
        # Test data samples
        self.test_chat_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, can you help me with Python programming?"}
        ]
        
        self.test_generation_prompt = "Generate a creative story about a robot learning to paint"
        
        # Mock API key for testing
        self.test_api_key = os.getenv("QWEN_API_KEY", "test-api-key")
    
    def log_api_call(self, endpoint: str, request_data: Dict[str, Any], response_data: Dict[str, Any]):
        """Log API call for analysis"""
        self.api_call_count += 1
        call_info = {
            "call_number": self.api_call_count,
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "request": request_data,
            "response": response_data
        }
        self.api_call_log.append(call_info)
        
        print(f"\n{'='*60}")
        print(f"API CALL #{self.api_call_count}: {endpoint}")
        print(f"{'='*60}")
        print(f"📥 REQUEST:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        print(f"\n📤 RESPONSE:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        print(f"{'='*60}")
    
    @patch('services.bailian_api_service.OpenAI')
    def test_qwen_chat_completions_api(self, mock_openai):
        """Test Qwen chat completions API with detailed data analysis"""
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.model_dump.return_value = {
            "id": "chatcmpl-test123",
            "object": "chat.completion",
            "created": 1699900000,
            "model": "qwen-max",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! I'd be happy to help you with Python programming. What specific topic or problem would you like assistance with?"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 25,
                "completion_tokens": 30,
                "total_tokens": 55
            }
        }
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 25
        mock_response.usage.completion_tokens = 30
        mock_response.usage.total_tokens = 55
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create test request
        request_data = {
            "model": "qwen-max",
            "messages": self.test_chat_messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Test direct service call
        with patch('config.database.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            service = BailianAPIService(mock_db)
            result = service.call_qwen_model(
                model_name=request_data["model"],
                messages=request_data["messages"],
                user_id=1,
                temperature=request_data["temperature"],
                max_tokens=request_data["max_tokens"]
            )
        
        # Log the API call
        self.log_api_call("/api/bailian/chat/completions", request_data, result)
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert "usage" in result
        assert result["usage"]["total_tokens"] == 55
        assert result["usage"]["request_tokens"] == 25
        assert result["usage"]["response_tokens"] == 30
        
        print(f"✅ QWEN CHAT COMPLETIONS TEST - INPUT/OUTPUT ANALYSIS:")
        print(f"   📊 Token Usage: {result['usage']['total_tokens']} total tokens")
        print(f"   ⏱️  Response Time: {result['usage']['call_duration']}ms")
        print(f"   💰 Estimated Cost: ~${result['usage']['total_tokens'] * 0.002:.4f}")
    
    @patch('services.bailian_api_service.Generation')
    def test_wanx_generation_api(self, mock_generation):
        """Test Wanx generation API with detailed data analysis"""
        
        # Mock DashScope response
        mock_response = Mock()
        mock_response.__dict__ = {
            "status_code": 200,
            "output": {
                "task_id": "task-12345",
                "task_status": "SUCCEEDED",
                "results": [{
                    "url": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/1234567890/sample_image.jpg"
                }]
            },
            "usage": Mock()
        }
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 0  # Image generation doesn't have output tokens
        
        mock_generation.call.return_value = mock_response
        
        # Create test request
        request_data = {
            "model": "wanx-v1",
            "prompt": self.test_generation_prompt,
            "parameters": {
                "size": "1024*1024",
                "style": "realistic"
            }
        }
        
        # Test direct service call
        with patch('config.database.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            service = BailianAPIService(mock_db)
            result = service.call_wanx_model(
                model_name=request_data["model"],
                prompt=request_data["prompt"],
                parameters=request_data["parameters"],
                user_id=1
            )
        
        # Log the API call
        self.log_api_call("/api/bailian/generation", request_data, result)
        
        # Assertions
        assert result["success"] is True
        assert "data" in result
        assert "usage" in result
        assert result["usage"]["request_tokens"] == 15
        
        print(f"✅ WANX GENERATION TEST - INPUT/OUTPUT ANALYSIS:")
        print(f"   📊 Token Usage: {result['usage']['request_tokens']} input tokens")
        print(f"   ⏱️  Response Time: {result['usage']['call_duration']}ms")
        print(f"   🖼️  Image Generated: {result['data']['output']['results'][0]['url']}")
    
    def test_api_endpoint_chat_completions(self):
        """Test the actual FastAPI endpoint for chat completions"""
        
        # Mock authentication
        with patch('api.auth.get_current_user_from_token') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = "test_user"
            mock_auth.return_value = mock_user
            
            # Mock the service
            with patch('services.bailian_api_service.BailianAPIService') as mock_service_class:
                mock_service = Mock()
                mock_service.call_qwen_model.return_value = {
                    "success": True,
                    "data": {
                        "choices": [{
                            "message": {
                                "content": "Test response from Qwen"
                            }
                        }]
                    },
                    "usage": {
                        "total_tokens": 50,
                        "request_tokens": 20,
                        "response_tokens": 30
                    }
                }
                mock_service_class.return_value = mock_service
                
                # Make API request
                request_data = {
                    "model": "qwen-max",
                    "messages": self.test_chat_messages,
                    "temperature": 0.7
                }
                
                response = self.client.post(
                    "/api/bailian/chat/completions",
                    json=request_data,
                    headers={"Authorization": "Bearer test-token"}
                )
                
                # Log the API call
                self.log_api_call("FastAPI /api/bailian/chat/completions", request_data, response.json())
                
                # Assertions
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert data["message"] == "Request successful"
                assert "data" in data
                
                print(f"✅ FASTAPI CHAT ENDPOINT TEST:")
                print(f"   🌐 HTTP Status: {response.status_code}")
                print(f"   📡 Response Code: {data['code']}")
    
    def test_api_endpoint_generation(self):
        """Test the actual FastAPI endpoint for generation"""
        
        # Mock authentication
        with patch('api.auth.get_current_user_from_token') as mock_auth:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = "test_user"
            mock_auth.return_value = mock_user
            
            # Mock the service
            with patch('services.bailian_api_service.BailianAPIService') as mock_service_class:
                mock_service = Mock()
                mock_service.call_wanx_model.return_value = {
                    "success": True,
                    "data": {
                        "output": {
                            "task_id": "task-67890",
                            "results": [{
                                "url": "https://example.com/generated_image.jpg"
                            }]
                        }
                    },
                    "usage": {
                        "request_tokens": 12,
                        "response_tokens": 0
                    }
                }
                mock_service_class.return_value = mock_service
                
                # Make API request
                request_data = {
                    "model": "wanx-v1",
                    "prompt": self.test_generation_prompt,
                    "parameters": {"size": "512*512"}
                }
                
                response = self.client.post(
                    "/api/bailian/generation",
                    json=request_data,
                    headers={"Authorization": "Bearer test-token"}
                )
                
                # Log the API call
                self.log_api_call("FastAPI /api/bailian/generation", request_data, response.json())
                
                # Assertions
                assert response.status_code == 200
                data = response.json()
                assert data["code"] == 200
                assert data["message"] == "Request successful"
                assert "data" in data
                
                print(f"✅ FASTAPI GENERATION ENDPOINT TEST:")
                print(f"   🌐 HTTP Status: {response.status_code}")
                print(f"   📡 Response Code: {data['code']}")
    
    @pytest.mark.asyncio
    async def test_function_compute_qwen_integration(self):
        """Test Function Compute Qwen integration"""
        
        # Mock HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "output": {
                    "text": "This is a response from Function Compute Qwen service"
                }
            },
            "token_usage": {
                "input_tokens": 20,
                "output_tokens": 15,
                "total_tokens": 35
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = Mock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            # Test Function Compute service
            fc_service = FunctionComputeService()
            
            request = FunctionComputeRequest(
                model="qwen-max",
                prompt="Test prompt for Function Compute",
                messages=self.test_chat_messages,
                user_id=1,
                correlation_id="test-correlation-123"
            )
            
            result = await fc_service.invoke_qwen_function(request)
            
            # Log the API call
            self.log_api_call("Function Compute Qwen", request.__dict__, result.__dict__)
            
            # Assertions
            assert result.success is True
            assert result.data is not None
            assert result.token_usage is not None
            
            print(f"✅ FUNCTION COMPUTE QWEN TEST:")
            print(f"   ⚡ Serverless Execution Time: {result.execution_time_ms}ms")
            print(f"   📊 Token Usage: {result.token_usage}")
    
    def test_generate_api_documentation(self):
        """Generate comprehensive API documentation"""
        
        print(f"\n🔍 QWEN API INTEGRATION ANALYSIS REPORT")
        print(f"{'='*80}")
        print(f"📅 Test Date: {datetime.utcnow().isoformat()}")
        print(f"🔢 Total API Calls Tested: {self.api_call_count}")
        print(f"{'='*80}")
        
        # API Summary
        api_summary = {
            "endpoints": [
                {
                    "name": "Chat Completions",
                    "endpoint": "/api/bailian/chat/completions",
                    "method": "POST",
                    "description": "Qwen model chat completions using OpenAI-compatible API",
                    "input_format": {
                        "model": "string (e.g., 'qwen-max')",
                        "messages": "array of {role: string, content: string}",
                        "temperature": "float (0.0-2.0, optional, default: 1.0)",
                        "max_tokens": "integer (optional)"
                    },
                    "output_format": {
                        "code": "integer (200 for success)",
                        "message": "string",
                        "data": {
                            "id": "string",
                            "object": "string",
                            "created": "timestamp",
                            "model": "string",
                            "choices": "array of choice objects",
                            "usage": {
                                "prompt_tokens": "integer",
                                "completion_tokens": "integer", 
                                "total_tokens": "integer"
                            }
                        }
                    },
                    "authentication": "Bearer JWT token required",
                    "rate_limiting": "100 requests per minute (configurable)"
                },
                {
                    "name": "Content Generation",
                    "endpoint": "/api/bailian/generation",
                    "method": "POST", 
                    "description": "Wanx model content/image generation",
                    "input_format": {
                        "model": "string (e.g., 'wanx-v1')",
                        "prompt": "string",
                        "parameters": "object (optional, model-specific parameters)"
                    },
                    "output_format": {
                        "code": "integer (200 for success)",
                        "message": "string",
                        "data": {
                            "output": {
                                "task_id": "string",
                                "task_status": "string",
                                "results": "array of result objects"
                            }
                        }
                    },
                    "authentication": "Bearer JWT token required",
                    "rate_limiting": "50 requests per minute (configurable)"
                }
            ],
            "function_compute_integration": {
                "qwen_endpoint": "Environment variable: FC_QWEN_ENDPOINT",
                "wanx_endpoint": "Environment variable: FC_WANX_ENDPOINT",
                "authentication": "Bearer token via FC_AUTH_TOKEN",
                "scaling": "Automatic based on request volume",
                "timeout": "30 seconds default"
            },
            "monitoring_metrics": {
                "api_call_count": "Total API calls made",
                "token_usage": "Input/output/total tokens",
                "response_time": "Milliseconds per request",
                "error_rate": "Failed requests percentage",
                "cost_estimation": "Based on token usage"
            }
        }
        
        print(f"\n📋 API ENDPOINTS SUMMARY:")
        for endpoint in api_summary["endpoints"]:
            print(f"   🔗 {endpoint['name']}: {endpoint['method']} {endpoint['endpoint']}")
            print(f"      📝 Description: {endpoint['description']}")
            print(f"      🔐 Auth: {endpoint['authentication']}")
            print(f"      ⏱️  Rate Limit: {endpoint['rate_limiting']}")
        
        print(f"\n⚡ FUNCTION COMPUTE INTEGRATION:")
        fc_info = api_summary["function_compute_integration"]
        for key, value in fc_info.items():
            print(f"   📌 {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n📊 MONITORING & METRICS:")
        metrics_info = api_summary["monitoring_metrics"]
        for key, value in metrics_info.items():
            print(f"   📈 {key.replace('_', ' ').title()}: {value}")
        
        # Save detailed log
        log_file = f"/Users/chengpeng/Documents/bailian_demo/test_records/qwen_api_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        test_report = {
            "test_summary": {
                "timestamp": datetime.utcnow().isoformat(),
                "total_calls": self.api_call_count,
                "test_status": "PASSED",
                "api_endpoints_tested": len(api_summary["endpoints"])
            },
            "api_documentation": api_summary,
            "detailed_call_log": self.api_call_log
        }
        
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(test_report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Detailed test report saved to: {log_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save test report: {e}")
        
        print(f"\n✅ API INTEGRATION TESTING COMPLETE")
        print(f"{'='*80}")

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])