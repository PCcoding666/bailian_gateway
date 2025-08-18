#!/usr/bin/env python3
"""
Comprehensive Test Suite for Specific Qwen Models
Tests: qwen-max, qwen-vl-max, wan2.2-t2i-plus
"""

import pytest
import requests
import json
import time
import os
from typing import Dict, Any, List
from datetime import datetime

# Test configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_USERNAME = os.getenv("TEST_USERNAME", "admin")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "AdminPass123!")

class QwenModelTester:
    """Comprehensive tester for specific Qwen models"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "models_tested": [],
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "estimated_cost": 0.0,
            "test_details": []
        }
    
    def authenticate(self) -> bool:
        """Authenticate and get access token"""
        print("🔐 Authenticating...")
        
        auth_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/auth/login", json=auth_data)
            
            if response.status_code == 200:
                auth_result = response.json()
                self.access_token = auth_result["data"]["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_qwen_max(self) -> Dict[str, Any]:
        """Test Qwen-Max model for advanced reasoning"""
        print("\n🧠 Testing Qwen-Max (Advanced Reasoning)...")
        
        test_cases = [
            {
                "name": "Simple Chat",
                "messages": [
                    {"role": "user", "content": "What is the capital of China?"}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            },
            {
                "name": "Complex Reasoning", 
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant specialized in logical reasoning."},
                    {"role": "user", "content": "If a train travels 60 mph for 2 hours, then 80 mph for 1.5 hours, what is the total distance traveled?"}
                ],
                "temperature": 0.3,
                "max_tokens": 200
            },
            {
                "name": "Multi-turn Conversation",
                "messages": [
                    {"role": "user", "content": "I'm planning a trip to Japan. Can you help me?"},
                    {"role": "assistant", "content": "I'd be happy to help you plan your trip to Japan! What specific aspects would you like assistance with?"},
                    {"role": "user", "content": "I want to visit Tokyo and Kyoto. What are the must-see attractions?"}
                ],
                "temperature": 0.8,
                "max_tokens": 500
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            request_data = {
                "model": "qwen-max",
                "messages": test_case["messages"],
                "temperature": test_case["temperature"],
                "max_tokens": test_case["max_tokens"]
            }
            
            start_time = time.time()
            
            try:
                response = self.session.post(f"{self.base_url}/api/bailian/chat/completions", json=request_data)
                duration = time.time() - start_time
                
                self.test_results["total_requests"] += 1
                
                if response.status_code == 200:
                    result = response.json()
                    self.test_results["successful_requests"] += 1
                    
                    # Extract usage information
                    usage = result.get("usage", {})
                    total_tokens = usage.get("total_tokens", 0)
                    estimated_cost = usage.get("estimated_cost", 0)
                    
                    self.test_results["total_tokens_used"] += total_tokens
                    self.test_results["estimated_cost"] += estimated_cost
                    
                    test_result = {
                        "test_case": test_case["name"],
                        "status": "SUCCESS",
                        "status_code": response.status_code,
                        "duration": duration,
                        "tokens_used": total_tokens,
                        "estimated_cost": estimated_cost,
                        "response_length": len(str(result.get("data", {}))),
                        "has_response": bool(result.get("data"))
                    }
                    
                    results.append(test_result)
                    print(f"    ✅ Success - {total_tokens} tokens, ${estimated_cost:.4f}")
                    
                else:
                    self.test_results["failed_requests"] += 1
                    test_result = {
                        "test_case": test_case["name"],
                        "status": "FAILED",
                        "status_code": response.status_code,
                        "duration": duration,
                        "error": response.text
                    }
                    
                    results.append(test_result)
                    print(f"    ❌ Failed - {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                self.test_results["failed_requests"] += 1
                test_result = {
                    "test_case": test_case["name"],
                    "status": "ERROR",
                    "duration": time.time() - start_time,
                    "error": str(e)
                }
                
                results.append(test_result)
                print(f"    ❌ Error - {str(e)}")
        
        return {"model": "qwen-max", "results": results}
    
    def test_qwen_vl_max(self) -> Dict[str, Any]:
        """Test Qwen-VL-Max model for multimodal understanding"""
        print("\n👁️ Testing Qwen-VL-Max (Multimodal Vision)...")
        
        test_cases = [
            {
                "name": "Text-only Chat",
                "messages": [
                    {"role": "user", "content": "Describe what you can do with vision capabilities."}
                ],
                "temperature": 0.7,
                "max_tokens": 200
            },
            {
                "name": "Multimodal Content",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What do you see in this image?"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "https://example.com/sample-image.jpg"  # Placeholder URL
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 300
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            # Test both endpoints for qwen-vl-max
            endpoints = [
                {"url": "/api/bailian/chat/completions", "name": "Chat Endpoint"},
                {"url": "/api/bailian/multimodal", "name": "Multimodal Endpoint"}
            ]
            
            for endpoint in endpoints:
                request_data = {
                    "model": "qwen-vl-max",
                    "messages": test_case["messages"],
                    "temperature": test_case["temperature"],
                    "max_tokens": test_case["max_tokens"]
                }
                
                start_time = time.time()
                
                try:
                    response = self.session.post(f"{self.base_url}{endpoint['url']}", json=request_data)
                    duration = time.time() - start_time
                    
                    self.test_results["total_requests"] += 1
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.test_results["successful_requests"] += 1
                        
                        usage = result.get("usage", {})
                        total_tokens = usage.get("total_tokens", 0)
                        estimated_cost = usage.get("estimated_cost", 0)
                        
                        self.test_results["total_tokens_used"] += total_tokens
                        self.test_results["estimated_cost"] += estimated_cost
                        
                        test_result = {
                            "test_case": f"{test_case['name']} - {endpoint['name']}",
                            "status": "SUCCESS",
                            "status_code": response.status_code,
                            "duration": duration,
                            "tokens_used": total_tokens,
                            "estimated_cost": estimated_cost,
                            "endpoint": endpoint["url"],
                            "has_response": bool(result.get("data"))
                        }
                        
                        results.append(test_result)
                        print(f"    ✅ {endpoint['name']} Success - {total_tokens} tokens, ${estimated_cost:.4f}")
                        
                    else:
                        self.test_results["failed_requests"] += 1
                        test_result = {
                            "test_case": f"{test_case['name']} - {endpoint['name']}",
                            "status": "FAILED",
                            "status_code": response.status_code,
                            "duration": duration,
                            "endpoint": endpoint["url"],
                            "error": response.text
                        }
                        
                        results.append(test_result)
                        print(f"    ❌ {endpoint['name']} Failed - {response.status_code}")
                        
                except Exception as e:
                    self.test_results["failed_requests"] += 1
                    test_result = {
                        "test_case": f"{test_case['name']} - {endpoint['name']}",
                        "status": "ERROR",
                        "duration": time.time() - start_time,
                        "endpoint": endpoint["url"],
                        "error": str(e)
                    }
                    
                    results.append(test_result)
                    print(f"    ❌ {endpoint['name']} Error - {str(e)}")
        
        return {"model": "qwen-vl-max", "results": results}
    
    def test_wan2_t2i_plus(self) -> Dict[str, Any]:
        """Test Wan2.2-T2I-Plus model for image generation"""
        print("\n🎨 Testing Wan2.2-T2I-Plus (Image Generation)...")
        
        test_cases = [
            {
                "name": "Simple Image Generation",
                "prompt": "A beautiful sunset over mountains",
                "parameters": {
                    "size": "1024*1024",
                    "quality": "high",
                    "style": "realistic"
                }
            },
            {
                "name": "Artistic Style",
                "prompt": "A cat wearing a hat in the style of Van Gogh",
                "parameters": {
                    "size": "1024*1024",
                    "quality": "high",
                    "style": "artistic"
                }
            },
            {
                "name": "Abstract Concept",
                "prompt": "The concept of time represented as a flowing river",
                "parameters": {
                    "size": "512*512",
                    "quality": "medium",
                    "style": "abstract"
                }
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"  Testing: {test_case['name']}")
            
            request_data = {
                "model": "wan2.2-t2i-plus",
                "prompt": test_case["prompt"],
                "parameters": test_case["parameters"]
            }
            
            start_time = time.time()
            
            try:
                response = self.session.post(f"{self.base_url}/api/bailian/generation", json=request_data)
                duration = time.time() - start_time
                
                self.test_results["total_requests"] += 1
                
                if response.status_code == 200:
                    result = response.json()
                    self.test_results["successful_requests"] += 1
                    
                    usage = result.get("usage", {})
                    estimated_cost = usage.get("estimated_cost", 0)
                    
                    self.test_results["estimated_cost"] += estimated_cost
                    
                    # Check if image generation was successful
                    data = result.get("data", {})
                    has_image_output = bool(data.get("output", {}).get("results"))
                    
                    test_result = {
                        "test_case": test_case["name"],
                        "status": "SUCCESS",
                        "status_code": response.status_code,
                        "duration": duration,
                        "estimated_cost": estimated_cost,
                        "has_image_output": has_image_output,
                        "prompt_length": len(test_case["prompt"])
                    }
                    
                    results.append(test_result)
                    print(f"    ✅ Success - ${estimated_cost:.4f}, Image: {has_image_output}")
                    
                else:
                    self.test_results["failed_requests"] += 1
                    test_result = {
                        "test_case": test_case["name"],
                        "status": "FAILED",
                        "status_code": response.status_code,
                        "duration": duration,
                        "error": response.text
                    }
                    
                    results.append(test_result)
                    print(f"    ❌ Failed - {response.status_code}")
                    
            except Exception as e:
                self.test_results["failed_requests"] += 1
                test_result = {
                    "test_case": test_case["name"],
                    "status": "ERROR",
                    "duration": time.time() - start_time,
                    "error": str(e)
                }
                
                results.append(test_result)
                print(f"    ❌ Error - {str(e)}")
        
        return {"model": "wan2.2-t2i-plus", "results": results}
    
    def test_model_status(self) -> Dict[str, Any]:
        """Test model status and capabilities endpoint"""
        print("\n📊 Testing Model Status Endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/bailian/models/status")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Model status retrieved successfully")
                
                # Validate expected models are present
                supported_models = result.get("supported_models", [])
                expected_models = ["qwen-max", "qwen-vl-max", "wan2.2-t2i-plus"]
                
                missing_models = [model for model in expected_models if model not in supported_models]
                
                if missing_models:
                    print(f"⚠️  Warning: Missing expected models: {missing_models}")
                else:
                    print("✅ All expected models are supported")
                
                return {
                    "status": "SUCCESS",
                    "supported_models": supported_models,
                    "api_key_configured": result.get("api_key_configured", False),
                    "service_status": result.get("service_status"),
                    "missing_models": missing_models
                }
            else:
                print(f"❌ Model status check failed: {response.status_code}")
                return {"status": "FAILED", "error": response.text}
                
        except Exception as e:
            print(f"❌ Model status error: {str(e)}")
            return {"status": "ERROR", "error": str(e)}
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite for all specific models"""
        print("🚀 Starting Comprehensive Qwen Models Test Suite")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            return {"error": "Authentication failed"}
        
        # Test model status
        status_result = self.test_model_status()
        
        # Test each model
        qwen_max_results = self.test_qwen_max()
        qwen_vl_results = self.test_qwen_vl_max()
        wan2_t2i_results = self.test_wan2_t2i_plus()
        
        # Compile final results
        self.test_results["models_tested"] = ["qwen-max", "qwen-vl-max", "wan2.2-t2i-plus"]
        self.test_results["test_details"] = [
            status_result,
            qwen_max_results,
            qwen_vl_results,
            wan2_t2i_results
        ]
        
        # Calculate success rate
        success_rate = (self.test_results["successful_requests"] / 
                       max(self.test_results["total_requests"], 1)) * 100
        
        self.test_results["success_rate"] = success_rate
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        print(f"🎯 Models Tested: {', '.join(self.test_results['models_tested'])}")
        print(f"📊 Total Requests: {self.test_results['total_requests']}")
        print(f"✅ Successful: {self.test_results['successful_requests']}")
        print(f"❌ Failed: {self.test_results['failed_requests']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"🪙 Total Tokens Used: {self.test_results['total_tokens_used']}")
        print(f"💰 Estimated Total Cost: ${self.test_results['estimated_cost']:.4f}")
        
        if success_rate >= 80:
            print("🎉 OVERALL STATUS: READY FOR CLOUD MIGRATION")
        else:
            print("⚠️  OVERALL STATUS: NEEDS ATTENTION BEFORE MIGRATION")
        
        return self.test_results
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qwen_models_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Test results saved to: {filename}")

def main():
    """Main test execution"""
    tester = QwenModelTester()
    results = tester.run_comprehensive_test()
    tester.save_results()
    
    return results

if __name__ == "__main__":
    main()