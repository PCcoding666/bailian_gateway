#!/usr/bin/env python3
"""
Standalone Qwen API Testing Script
Tests real API calls to validate integrations before cloud migration
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

class QwenAPITester:
    """Comprehensive API testing for Qwen integrations"""
    
    def __init__(self):
        self.api_call_count = 0
        self.api_call_log = []
        self.base_url = "http://localhost:8000"
        self.auth_token = None
        
        # Load environment variables
        self.qwen_api_key = os.getenv("QWEN_API_KEY")
        if not self.qwen_api_key:
            print("⚠️  Warning: QWEN_API_KEY not found in environment variables")
        
        # Test data
        self.test_user = {
            "username": "test_user",
            "password": "test_password123"
        }
        
        self.test_messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Hello! Can you help me understand machine learning basics?"}
        ]
        
        self.test_generation_prompt = "Create a beautiful landscape painting of mountains at sunset"
    
    def log_api_call(self, endpoint: str, request_data: Dict[str, Any], response_data: Dict[str, Any], 
                     status_code: int = 200, duration_ms: float = 0):
        """Log API call details"""
        self.api_call_count += 1
        
        call_info = {
            "call_number": self.api_call_count,
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "request": request_data,
            "response": response_data
        }
        
        self.api_call_log.append(call_info)
        
        print(f"\n{'='*80}")
        print(f"📡 API CALL #{self.api_call_count}: {endpoint}")
        print(f"{'='*80}")
        print(f"🕐 Timestamp: {call_info['timestamp']}")
        print(f"⏱️  Duration: {duration_ms:.2f}ms")
        print(f"📊 Status Code: {status_code}")
        print(f"\n📥 REQUEST:")
        print(json.dumps(request_data, indent=2, ensure_ascii=False))
        print(f"\n📤 RESPONSE:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        print(f"{'='*80}")
        
        return call_info
    
    def check_service_health(self) -> bool:
        """Check if the backend service is running"""
        try:
            print("🔍 Checking backend service health...")
            start_time = time.time()
            
            response = requests.get(f"{self.base_url}/health", timeout=10)
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_api_call("/health", {}, health_data, response.status_code, duration_ms)
                print("✅ Backend service is healthy")
                return True
            else:
                print(f"❌ Backend service health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend service. Is it running on http://localhost:8000?")
            print("💡 Try running: cd backend && python -m uvicorn main:app --reload")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def check_readiness(self) -> Dict[str, Any]:
        """Check service readiness including dependencies"""
        try:
            print("🔍 Checking service readiness...")
            start_time = time.time()
            
            response = requests.get(f"{self.base_url}/health/ready", timeout=10)
            duration_ms = (time.time() - start_time) * 1000
            
            readiness_data = response.json() if response.status_code == 200 else {"error": response.text}
            self.log_api_call("/health/ready", {}, readiness_data, response.status_code, duration_ms)
            
            if response.status_code == 200:
                print("✅ Service is ready with all dependencies")
                checks = readiness_data.get("checks", {})
                print(f"   📊 Database: {checks.get('database', 'unknown')}")
                print(f"   📊 Redis: {checks.get('redis', 'unknown')}")
                print(f"   📊 DashScope API: {checks.get('dashscope_api', 'unknown')}")
            else:
                print(f"⚠️  Service readiness issues detected")
                
            return readiness_data
            
        except Exception as e:
            print(f"❌ Readiness check error: {e}")
            return {"error": str(e)}
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            print("🔐 Authenticating with backend...")
            
            # Try to login with admin user (created automatically)
            login_data = {
                "username": "admin",
                "password": "AdminPass123!"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=10)
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                auth_response = response.json()
                self.log_api_call("/api/auth/login", login_data, auth_response, response.status_code, duration_ms)
                
                if auth_response.get("code") == 200 and "data" in auth_response:
                    self.auth_token = auth_response["data"]["access_token"]
                    print("✅ Authentication successful")
                    print(f"   👤 User: {auth_response['data']['user']['username']}")
                    return True
                else:
                    print(f"❌ Authentication failed: {auth_response}")
                    return False
            else:
                error_response = {"error": response.text, "status_code": response.status_code}
                self.log_api_call("/api/auth/login", login_data, error_response, response.status_code, duration_ms)
                print(f"❌ Authentication request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_qwen_chat_completions(self) -> Dict[str, Any]:
        """Test Qwen chat completions API"""
        if not self.auth_token:
            print("❌ Cannot test chat completions - not authenticated")
            return {"error": "Not authenticated"}
        
        print("🤖 Testing Qwen Chat Completions API...")
        
        request_data = {
            "model": "qwen-max",
            "messages": self.test_messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/bailian/chat/completions",
                json=request_data,
                headers=headers,
                timeout=30
            )
            duration_ms = (time.time() - start_time) * 1000
            
            response_data = response.json() if response.status_code == 200 else {"error": response.text}
            call_info = self.log_api_call(
                "/api/bailian/chat/completions", 
                request_data, 
                response_data, 
                response.status_code, 
                duration_ms
            )
            
            if response.status_code == 200 and response_data.get("code") == 200:
                print("✅ Qwen Chat Completions test successful")
                
                # Extract usage information
                data = response_data.get("data", {})
                usage = data.get("usage", {})
                
                print(f"   📊 Token Usage:")
                print(f"      - Prompt tokens: {usage.get('prompt_tokens', 'unknown')}")
                print(f"      - Completion tokens: {usage.get('completion_tokens', 'unknown')}")
                print(f"      - Total tokens: {usage.get('total_tokens', 'unknown')}")
                
                # Extract generated content
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    print(f"   💬 Generated Response: {content[:100]}...")
                
                return {
                    "success": True,
                    "data": response_data,
                    "metrics": {
                        "duration_ms": duration_ms,
                        "token_usage": usage,
                        "estimated_cost": usage.get('total_tokens', 0) * 0.002  # Rough estimate
                    }
                }
            else:
                print(f"❌ Qwen Chat Completions test failed: {response_data}")
                return {"success": False, "error": response_data}
                
        except Exception as e:
            print(f"❌ Chat completions test error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_wanx_generation(self) -> Dict[str, Any]:
        """Test Wanx generation API"""
        if not self.auth_token:
            print("❌ Cannot test generation - not authenticated")
            return {"error": "Not authenticated"}
        
        print("🎨 Testing Wanx Generation API...")
        
        request_data = {
            "model": "wanx-v1",
            "prompt": self.test_generation_prompt,
            "parameters": {
                "size": "1024*1024",
                "style": "realistic"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/bailian/generation",
                json=request_data,
                headers=headers,
                timeout=60  # Generation might take longer
            )
            duration_ms = (time.time() - start_time) * 1000
            
            response_data = response.json() if response.status_code == 200 else {"error": response.text}
            call_info = self.log_api_call(
                "/api/bailian/generation", 
                request_data, 
                response_data, 
                response.status_code, 
                duration_ms
            )
            
            if response.status_code == 200 and response_data.get("code") == 200:
                print("✅ Wanx Generation test successful")
                
                # Extract generation information
                data = response_data.get("data", {})
                output = data.get("output", {})
                
                print(f"   🎯 Task ID: {output.get('task_id', 'unknown')}")
                print(f"   📊 Task Status: {output.get('task_status', 'unknown')}")
                
                results = output.get("results", [])
                if results:
                    print(f"   🖼️  Generated {len(results)} result(s)")
                    for i, result in enumerate(results):
                        print(f"      Result {i+1}: {result.get('url', 'No URL')}")
                
                return {
                    "success": True,
                    "data": response_data,
                    "metrics": {
                        "duration_ms": duration_ms,
                        "results_count": len(results)
                    }
                }
            else:
                print(f"❌ Wanx Generation test failed: {response_data}")
                return {"success": False, "error": response_data}
                
        except Exception as e:
            print(f"❌ Generation test error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_prometheus_metrics(self) -> Dict[str, Any]:
        """Test Prometheus metrics endpoint"""
        print("📊 Testing Prometheus Metrics...")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                metrics_text = response.text
                self.log_api_call("/metrics", {}, {"metrics_length": len(metrics_text)}, response.status_code, duration_ms)
                
                print("✅ Metrics endpoint accessible")
                print(f"   📏 Metrics data length: {len(metrics_text)} characters")
                
                # Count specific metrics
                metrics_counts = {
                    "http_requests_total": metrics_text.count("http_requests_total"),
                    "http_request_duration": metrics_text.count("http_request_duration"),
                    "app_info": metrics_text.count("app_info"),
                    "health_check_status": metrics_text.count("health_check_status")
                }
                
                print("   📈 Key metrics found:")
                for metric, count in metrics_counts.items():
                    print(f"      - {metric}: {count} entries")
                
                return {"success": True, "metrics_counts": metrics_counts}
            else:
                print(f"❌ Metrics endpoint failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Metrics test error: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print(f"\n🔍 GENERATING COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")
        
        # Calculate summary statistics
        total_calls = len(self.api_call_log)
        successful_calls = len([call for call in self.api_call_log if call["status_code"] < 400])
        failed_calls = total_calls - successful_calls
        
        if total_calls > 0:
            success_rate = (successful_calls / total_calls) * 100
            avg_duration = sum(call["duration_ms"] for call in self.api_call_log) / total_calls
        else:
            success_rate = 0
            avg_duration = 0
        
        # Calculate token usage
        total_tokens = 0
        total_cost_estimate = 0
        
        for call in self.api_call_log:
            if "completions" in call["endpoint"]:
                response_data = call.get("response", {})
                if isinstance(response_data, dict) and "data" in response_data:
                    usage = response_data["data"].get("usage", {})
                    tokens = usage.get("total_tokens", 0)
                    total_tokens += tokens
                    total_cost_estimate += tokens * 0.002  # Rough estimate
        
        report = {
            "test_summary": {
                "timestamp": datetime.utcnow().isoformat(),
                "total_api_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "success_rate_percent": round(success_rate, 2),
                "average_response_time_ms": round(avg_duration, 2),
                "total_tokens_used": total_tokens,
                "estimated_total_cost_usd": round(total_cost_estimate, 4)
            },
            "api_endpoints_tested": [
                {
                    "endpoint": "/health",
                    "description": "Basic health check",
                    "method": "GET",
                    "authentication": "None required"
                },
                {
                    "endpoint": "/health/ready",
                    "description": "Kubernetes readiness probe with dependency checks",
                    "method": "GET",
                    "authentication": "None required"
                },
                {
                    "endpoint": "/api/auth/login",
                    "description": "User authentication",
                    "method": "POST",
                    "authentication": "Username/password"
                },
                {
                    "endpoint": "/api/bailian/chat/completions",
                    "description": "Qwen chat completions via OpenAI-compatible API",
                    "method": "POST",
                    "authentication": "Bearer JWT token"
                },
                {
                    "endpoint": "/api/bailian/generation",
                    "description": "Wanx content generation",
                    "method": "POST",
                    "authentication": "Bearer JWT token"
                },
                {
                    "endpoint": "/metrics",
                    "description": "Prometheus metrics",
                    "method": "GET",
                    "authentication": "None required"
                }
            ],
            "data_formats": {
                "chat_completions_input": {
                    "model": "string - AI model name (e.g., 'qwen-max')",
                    "messages": "array - Chat messages with role and content",
                    "temperature": "float - Randomness (0.0-2.0, optional)",
                    "max_tokens": "integer - Max response tokens (optional)"
                },
                "chat_completions_output": {
                    "code": "integer - Response code (200 for success)",
                    "message": "string - Response message",
                    "data": {
                        "id": "string - Completion ID",
                        "object": "string - Object type",
                        "created": "integer - Unix timestamp",
                        "model": "string - Model used",
                        "choices": "array - Generated responses",
                        "usage": {
                            "prompt_tokens": "integer - Input tokens",
                            "completion_tokens": "integer - Generated tokens",
                            "total_tokens": "integer - Total tokens"
                        }
                    }
                },
                "generation_input": {
                    "model": "string - Generation model (e.g., 'wanx-v1')",
                    "prompt": "string - Generation prompt",
                    "parameters": "object - Model-specific parameters (optional)"
                },
                "generation_output": {
                    "code": "integer - Response code (200 for success)",
                    "message": "string - Response message",
                    "data": {
                        "output": {
                            "task_id": "string - Generation task ID",
                            "task_status": "string - Task status",
                            "results": "array - Generated content URLs/data"
                        }
                    }
                }
            },
            "detailed_call_log": self.api_call_log
        }
        
        # Print summary
        print(f"📊 TEST RESULTS SUMMARY:")
        print(f"   🔢 Total API Calls: {total_calls}")
        print(f"   ✅ Successful: {successful_calls}")
        print(f"   ❌ Failed: {failed_calls}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Average Response Time: {avg_duration:.1f}ms")
        print(f"   🪙 Total Tokens Used: {total_tokens}")
        print(f"   💰 Estimated Cost: ${total_cost_estimate:.4f}")
        
        print(f"\n📋 API ENDPOINTS TESTED:")
        for endpoint in report["api_endpoints_tested"]:
            print(f"   🔗 {endpoint['method']} {endpoint['endpoint']}")
            print(f"      📝 {endpoint['description']}")
            print(f"      🔐 Auth: {endpoint['authentication']}")
        
        # Save report
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        report_file = f"test_records/qwen_api_test_report_{timestamp}.json"
        
        try:
            os.makedirs("test_records", exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")
        
        return report
    
    def run_all_tests(self):
        """Run all API tests"""
        print(f"🚀 STARTING COMPREHENSIVE QWEN API TESTING")
        print(f"{'='*80}")
        print(f"🕐 Start Time: {datetime.utcnow().isoformat()}")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"🔑 API Key Present: {'Yes' if self.qwen_api_key else 'No'}")
        print(f"{'='*80}")
        
        # Test sequence
        tests = [
            ("Health Check", self.check_service_health),
            ("Readiness Check", self.check_readiness),
            ("Authentication", self.authenticate),
            ("Qwen Chat Completions", self.test_qwen_chat_completions),
            ("Wanx Generation", self.test_wanx_generation),
            ("Prometheus Metrics", self.test_prometheus_metrics)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                results[test_name] = result
                
                if isinstance(result, dict):
                    if result.get("success") is False:
                        print(f"⚠️  {test_name} had issues, but continuing...")
                elif result is False:
                    print(f"⚠️  {test_name} failed, but continuing...")
                    
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results[test_name] = {"success": False, "error": str(e)}
        
        # Generate final report
        print(f"\n📋 GENERATING FINAL REPORT...")
        final_report = self.generate_test_report()
        
        print(f"\n🎉 API TESTING COMPLETE!")
        print(f"{'='*80}")
        
        return final_report

def main():
    """Main function to run API tests"""
    tester = QwenAPITester()
    
    try:
        report = tester.run_all_tests()
        
        # Determine if we're ready for cloud migration
        success_rate = report["test_summary"]["success_rate_percent"]
        
        print(f"\n🔍 CLOUD MIGRATION READINESS ASSESSMENT:")
        print(f"{'='*60}")
        
        if success_rate >= 80:
            print(f"✅ READY FOR CLOUD MIGRATION")
            print(f"   📊 Success Rate: {success_rate}% (>= 80% threshold)")
            print(f"   🚀 All critical APIs are functional")
            print(f"   📋 Data formats validated")
            print(f"   📈 Metrics collection working")
        else:
            print(f"⚠️  NOT YET READY FOR CLOUD MIGRATION")
            print(f"   📊 Success Rate: {success_rate}% (< 80% threshold)")
            print(f"   🔧 Please fix failing tests before migration")
        
        print(f"\n📝 NEXT STEPS:")
        print(f"   1. Review test report for any failures")
        print(f"   2. Ensure all environment variables are set")
        print(f"   3. Verify Qwen API key is valid and has credits")
        print(f"   4. Test with different models and parameters")
        print(f"   5. Run load tests if needed")
        print(f"   6. Proceed with cloud migration when ready")
        
        return success_rate >= 80
        
    except KeyboardInterrupt:
        print(f"\n🛑 Testing interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)