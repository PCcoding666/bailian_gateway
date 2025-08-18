#!/usr/bin/env python3
"""
Integration Testing Suite for Bailian Demo
End-to-end testing in Alibaba Cloud environment
"""

import asyncio
import aiohttp
import json
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestStep:
    """Individual test step"""
    name: str
    method: str
    endpoint: str
    data: Optional[Dict] = None
    headers: Optional[Dict] = None
    expected_status: int = 200
    validation_func: Optional[callable] = None

@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    description: str
    steps: List[TestStep]
    dependencies: List[str] = None

class IntegrationTester:
    """Comprehensive integration testing framework"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.test_results = {}
        self.access_token = None
        self.test_data = {}
    
    async def setup(self):
        """Setup test environment"""
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        # Authenticate
        await self.authenticate()
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate and get access token"""
        auth_data = {
            "username": os.getenv("TEST_USERNAME", "admin"),
            "password": os.getenv("TEST_PASSWORD", "AdminPass123!")
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/auth/login", json=auth_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result["data"]["access_token"]
                    print("✅ Authentication successful")
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status}")
        except Exception as e:
            print(f"❌ Authentication error: {e}")
        return False
    
    async def execute_step(self, step: TestStep) -> Dict[str, Any]:
        """Execute individual test step"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if step.headers:
            headers.update(step.headers)
        
        start_time = time.time()
        
        try:
            url = f"{self.base_url}{step.endpoint}"
            
            if step.method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif step.method.upper() == "POST":
                async with self.session.post(url, json=step.data, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif step.method.upper() == "PUT":
                async with self.session.put(url, json=step.data, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif step.method.upper() == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            
            duration = time.time() - start_time
            
            # Validate response
            status_ok = response.status == step.expected_status
            validation_ok = True
            validation_message = ""
            
            if step.validation_func:
                try:
                    validation_ok = step.validation_func(response_data)
                    validation_message = "Custom validation passed" if validation_ok else "Custom validation failed"
                except Exception as e:
                    validation_ok = False
                    validation_message = f"Validation error: {str(e)}"
            
            success = status_ok and validation_ok
            
            return {
                "step_name": step.name,
                "success": success,
                "status_code": response.status,
                "expected_status": step.expected_status,
                "response_time": duration,
                "response_data": response_data,
                "validation_message": validation_message,
                "error": None
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                "step_name": step.name,
                "success": False,
                "status_code": 0,
                "expected_status": step.expected_status,
                "response_time": duration,
                "response_data": None,
                "validation_message": "",
                "error": str(e)
            }
    
    async def run_test_suite(self, suite: TestSuite) -> Dict[str, Any]:
        """Run complete test suite"""
        print(f"🧪 Running test suite: {suite.name}")
        
        suite_results = {
            "suite_name": suite.name,
            "description": suite.description,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "summary": {
                "total_steps": len(suite.steps),
                "passed_steps": 0,
                "failed_steps": 0,
                "success_rate": 0,
                "total_duration": 0
            }
        }
        
        suite_start_time = time.time()
        
        for step in suite.steps:
            print(f"  🔸 {step.name}...")
            step_result = await self.execute_step(step)
            suite_results["steps"].append(step_result)
            
            if step_result["success"]:
                suite_results["summary"]["passed_steps"] += 1
                print(f"    ✅ Passed ({step_result['response_time']:.2f}s)")
            else:
                suite_results["summary"]["failed_steps"] += 1
                print(f"    ❌ Failed: {step_result.get('error', 'Status/validation error')}")
            
            # Store data for subsequent steps
            if step_result["success"] and step_result["response_data"]:
                self.test_data[step.name] = step_result["response_data"]
        
        suite_duration = time.time() - suite_start_time
        suite_results["summary"]["total_duration"] = suite_duration
        suite_results["summary"]["success_rate"] = (
            suite_results["summary"]["passed_steps"] / suite_results["summary"]["total_steps"] * 100
            if suite_results["summary"]["total_steps"] > 0 else 0
        )
        suite_results["end_time"] = datetime.now().isoformat()
        
        return suite_results

def create_integration_test_suites() -> List[TestSuite]:
    """Create comprehensive integration test suites"""
    
    # Health and System Tests
    health_suite = TestSuite(
        name="Health and System Tests",
        description="Test basic system health and monitoring endpoints",
        steps=[
            TestStep("Basic Health Check", "GET", "/health"),
            TestStep("Readiness Probe", "GET", "/health/ready"),
            TestStep("Liveness Probe", "GET", "/health/live"),
            TestStep("Security Health", "GET", "/health/security"),
            TestStep("Metrics Endpoint", "GET", "/metrics"),
        ]
    )
    
    # Authentication Tests
    auth_suite = TestSuite(
        name="Authentication Tests",
        description="Test user authentication and authorization",
        steps=[
            TestStep("Login", "POST", "/api/auth/login", {
                "username": "admin",
                "password": "AdminPass123!"
            }),
            TestStep("Token Validation", "GET", "/api/auth/me"),
            TestStep("Invalid Login", "POST", "/api/auth/login", {
                "username": "invalid",
                "password": "invalid"
            }, expected_status=401),
        ]
    )
    
    # AI Models Integration Tests
    ai_models_suite = TestSuite(
        name="AI Models Integration Tests", 
        description="Test Qwen models integration and functionality",
        steps=[
            TestStep("Model Status", "GET", "/api/bailian/models/status"),
            TestStep("Supported Models", "GET", "/api/bailian/models/supported"),
            TestStep("Qwen-Max Chat", "POST", "/api/bailian/chat/completions", {
                "model": "qwen-max",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "temperature": 0.7,
                "max_tokens": 100
            }),
            TestStep("Qwen-VL-Max Multimodal", "POST", "/api/bailian/multimodal", {
                "model": "qwen-vl-max", 
                "messages": [{"role": "user", "content": "Describe AI capabilities"}],
                "temperature": 0.5
            }),
            TestStep("Wan2.2-T2I-Plus Generation", "POST", "/api/bailian/generation", {
                "model": "wan2.2-t2i-plus",
                "prompt": "A simple test image",
                "parameters": {"size": "512*512", "quality": "medium"}
            }),
        ]
    )
    
    # Database Integration Tests  
    db_suite = TestSuite(
        name="Database Integration Tests",
        description="Test database connectivity and operations",
        steps=[
            TestStep("Database Health Check", "GET", "/health/ready", 
                    validation_func=lambda data: "database" in data.get("checks", {}) and 
                                                data["checks"]["database"] == "connected"),
        ]
    )
    
    # Cache Integration Tests
    cache_suite = TestSuite(
        name="Cache Integration Tests", 
        description="Test Redis cache functionality",
        steps=[
            TestStep("Cache Health Check", "GET", "/health/ready",
                    validation_func=lambda data: "redis" in data.get("checks", {}) and
                                                data["checks"]["redis"] == "connected"),
        ]
    )
    
    # Security Integration Tests
    security_suite = TestSuite(
        name="Security Integration Tests",
        description="Test security middleware and features",
        steps=[
            TestStep("Security Status", "GET", "/health/security"),
            TestStep("Security Metrics", "GET", "/health/security/metrics"),
            TestStep("Rate Limiting Test", "GET", "/health", validation_func=lambda data: True),
            TestStep("Unauthorized Access", "GET", "/api/bailian/models/status", 
                    headers={"Authorization": "Bearer invalid-token"}, expected_status=401),
        ]
    )
    
    return [health_suite, auth_suite, ai_models_suite, db_suite, cache_suite, security_suite]

async def main():
    """Main integration testing execution"""
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    print("🧪 Bailian Demo Integration Testing Suite")
    print("=" * 60)
    print(f"Testing against: {base_url}")
    print()
    
    tester = IntegrationTester(base_url)
    await tester.setup()
    
    try:
        test_suites = create_integration_test_suites()
        all_results = []
        
        total_suites = len(test_suites)
        overall_passed = 0
        overall_total = 0
        
        for i, suite in enumerate(test_suites, 1):
            print(f"📋 Test Suite {i}/{total_suites}")
            result = await tester.run_test_suite(suite)
            all_results.append(result)
            
            overall_passed += result["summary"]["passed_steps"]
            overall_total += result["summary"]["total_steps"]
            
            print(f"   Success Rate: {result['summary']['success_rate']:.1f}%")
            print(f"   Duration: {result['summary']['total_duration']:.2f}s")
            print()
        
        # Generate final report
        overall_success_rate = (overall_passed / overall_total * 100) if overall_total > 0 else 0
        
        final_report = {
            "test_timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "overall_summary": {
                "total_suites": total_suites,
                "total_steps": overall_total,
                "passed_steps": overall_passed,
                "failed_steps": overall_total - overall_passed,
                "overall_success_rate": overall_success_rate
            },
            "suite_results": all_results,
            "cloud_readiness": {
                "ready_for_production": overall_success_rate >= 90,
                "critical_issues": overall_success_rate < 80,
                "recommendations": []
            }
        }
        
        # Add recommendations based on results
        if overall_success_rate < 90:
            final_report["cloud_readiness"]["recommendations"].append(
                "Address failing tests before production deployment"
            )
        if overall_success_rate >= 95:
            final_report["cloud_readiness"]["recommendations"].append(
                "System is ready for cloud production deployment"
            )
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"integration_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        # Print summary
        print("=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"🎯 Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"✅ Passed Steps: {overall_passed}/{overall_total}")
        print(f"❌ Failed Steps: {overall_total - overall_passed}/{overall_total}")
        print(f"📄 Report saved: {report_file}")
        
        if final_report["cloud_readiness"]["ready_for_production"]:
            print("🚀 Status: READY FOR CLOUD PRODUCTION")
        elif final_report["cloud_readiness"]["critical_issues"]:
            print("⚠️  Status: CRITICAL ISSUES - NOT READY")
        else:
            print("🛠️  Status: MINOR ISSUES - REVIEW NEEDED")
        
        print()
        for rec in final_report["cloud_readiness"]["recommendations"]:
            print(f"💡 {rec}")
        
    finally:
        await tester.teardown()

if __name__ == "__main__":
    asyncio.run(main())