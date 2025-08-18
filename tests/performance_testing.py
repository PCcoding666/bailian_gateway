#!/usr/bin/env python3
"""
Performance Testing Suite for Bailian Demo
Load testing, stress testing, and performance optimization
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import concurrent.futures
import os
import subprocess

@dataclass
class TestConfig:
    """Performance test configuration"""
    base_url: str
    concurrent_users: int
    test_duration: int  # seconds
    ramp_up_time: int   # seconds
    endpoints: List[str]

@dataclass
class TestResult:
    """Test result metrics"""
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    requests_per_second: float
    error_rate: float

class PerformanceTester:
    """Comprehensive performance testing framework"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.results = []
        self.access_token = None
    
    async def authenticate(self) -> bool:
        """Authenticate and get access token"""
        auth_data = {
            "username": os.getenv("TEST_USERNAME", "admin"),
            "password": os.getenv("TEST_PASSWORD", "AdminPass123!")
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.config.base_url}/api/auth/login", json=auth_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.access_token = result["data"]["access_token"]
                        return True
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
        return False
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str) -> Dict[str, Any]:
        """Make HTTP request and measure performance"""
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        start_time = time.time()
        
        try:
            async with session.get(f"{self.config.base_url}{endpoint}", headers=headers) as response:
                await response.text()  # Ensure response is fully read
                duration = time.time() - start_time
                
                return {
                    "endpoint": endpoint,
                    "status_code": response.status,
                    "response_time": duration,
                    "success": 200 <= response.status < 400
                }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "response_time": duration,
                "success": False,
                "error": str(e)
            }
    
    async def load_test_endpoint(self, endpoint: str) -> TestResult:
        """Perform load test on specific endpoint"""
        print(f"🔄 Load testing {endpoint}...")
        
        requests_data = []
        connector = aiohttp.TCPConnector(limit=self.config.concurrent_users * 2)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            start_time = time.time()
            
            # Ramp up users gradually
            tasks = []
            for i in range(self.config.concurrent_users):
                await asyncio.sleep(self.config.ramp_up_time / self.config.concurrent_users)
                task = self.user_simulation(session, endpoint, start_time)
                tasks.append(task)
            
            # Execute all user simulations
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect all request data
            for result in results:
                if isinstance(result, list):
                    requests_data.extend(result)
        
        return self.analyze_results(endpoint, requests_data)
    
    async def user_simulation(self, session: aiohttp.ClientSession, endpoint: str, start_time: float) -> List[Dict]:
        """Simulate individual user load"""
        user_requests = []
        
        while time.time() - start_time < self.config.test_duration:
            request_result = await self.make_request(session, endpoint)
            user_requests.append(request_result)
            
            # Add small delay between requests (realistic user behavior)
            await asyncio.sleep(0.1)
        
        return user_requests
    
    def analyze_results(self, endpoint: str, requests_data: List[Dict]) -> TestResult:
        """Analyze performance test results"""
        if not requests_data:
            return TestResult(endpoint, 0, 0, 0, 0, 0, 0, 0, 0, 100)
        
        total_requests = len(requests_data)
        successful_requests = sum(1 for r in requests_data if r["success"])
        failed_requests = total_requests - successful_requests
        
        response_times = [r["response_time"] for r in requests_data]
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Calculate 95th percentile
        sorted_times = sorted(response_times)
        p95_index = int(0.95 * len(sorted_times))
        p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
        
        requests_per_second = total_requests / self.config.test_duration
        error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        
        return TestResult(
            endpoint=endpoint,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate
        )
    
    async def run_performance_tests(self) -> List[TestResult]:
        """Run performance tests on all endpoints"""
        print("🚀 Starting Performance Tests...")
        print(f"Configuration: {self.config.concurrent_users} users, {self.config.test_duration}s duration")
        
        # Authenticate first
        if not await self.authenticate():
            print("❌ Authentication failed, running tests without auth")
        
        results = []
        for endpoint in self.config.endpoints:
            result = await self.load_test_endpoint(endpoint)
            results.append(result)
            
            print(f"✅ {endpoint}: {result.requests_per_second:.1f} RPS, "
                  f"{result.avg_response_time*1000:.0f}ms avg, "
                  f"{result.error_rate:.1f}% errors")
        
        return results
    
    def generate_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        total_requests = sum(r.total_requests for r in results)
        total_successful = sum(r.successful_requests for r in results)
        total_failed = sum(r.failed_requests for r in results)
        
        avg_rps = statistics.mean([r.requests_per_second for r in results])
        avg_response_time = statistics.mean([r.avg_response_time for r in results])
        overall_error_rate = (total_failed / total_requests * 100) if total_requests > 0 else 0
        
        report = {
            "test_configuration": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": self.config.test_duration,
                "ramp_up_time": self.config.ramp_up_time,
                "endpoints_tested": len(self.config.endpoints)
            },
            "overall_metrics": {
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "failed_requests": total_failed,
                "overall_error_rate": overall_error_rate,
                "average_rps": avg_rps,
                "average_response_time_ms": avg_response_time * 1000
            },
            "endpoint_results": [
                {
                    "endpoint": r.endpoint,
                    "requests_per_second": r.requests_per_second,
                    "avg_response_time_ms": r.avg_response_time * 1000,
                    "p95_response_time_ms": r.p95_response_time * 1000,
                    "error_rate": r.error_rate,
                    "total_requests": r.total_requests
                }
                for r in results
            ],
            "performance_grade": self.calculate_performance_grade(results),
            "recommendations": self.generate_recommendations(results)
        }
        
        return report
    
    def calculate_performance_grade(self, results: List[TestResult]) -> str:
        """Calculate overall performance grade"""
        avg_response_time = statistics.mean([r.avg_response_time for r in results])
        avg_error_rate = statistics.mean([r.error_rate for r in results])
        
        if avg_response_time < 0.2 and avg_error_rate < 1:
            return "A+ (Excellent)"
        elif avg_response_time < 0.5 and avg_error_rate < 2:
            return "A (Very Good)"
        elif avg_response_time < 1.0 and avg_error_rate < 5:
            return "B (Good)"
        elif avg_response_time < 2.0 and avg_error_rate < 10:
            return "C (Acceptable)"
        else:
            return "D (Needs Improvement)"
    
    def generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        slow_endpoints = [r for r in results if r.avg_response_time > 1.0]
        if slow_endpoints:
            recommendations.append("Consider optimizing slow endpoints with caching or database query optimization")
        
        high_error_endpoints = [r for r in results if r.error_rate > 5]
        if high_error_endpoints:
            recommendations.append("Investigate and fix endpoints with high error rates")
        
        if any(r.requests_per_second < 10 for r in results):
            recommendations.append("Consider horizontal scaling or performance tuning for low-throughput endpoints")
        
        return recommendations

def create_test_scenarios() -> List[TestConfig]:
    """Create different test scenarios"""
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    return [
        # Light load test
        TestConfig(
            base_url=base_url,
            concurrent_users=10,
            test_duration=30,
            ramp_up_time=5,
            endpoints=["/health", "/health/ready", "/metrics"]
        ),
        
        # Medium load test
        TestConfig(
            base_url=base_url,
            concurrent_users=50,
            test_duration=60,
            ramp_up_time=10,
            endpoints=["/api/bailian/models/status", "/health", "/metrics"]
        ),
        
        # Heavy load test
        TestConfig(
            base_url=base_url,
            concurrent_users=100,
            test_duration=120,
            ramp_up_time=20,
            endpoints=["/health", "/health/ready", "/health/security"]
        )
    ]

async def main():
    """Main performance testing execution"""
    print("🔧 Bailian Demo Performance Testing Suite")
    print("=" * 50)
    
    test_scenarios = create_test_scenarios()
    all_reports = []
    
    for i, config in enumerate(test_scenarios, 1):
        print(f"\n📊 Running Test Scenario {i}/{len(test_scenarios)}")
        print(f"Users: {config.concurrent_users}, Duration: {config.test_duration}s")
        
        tester = PerformanceTester(config)
        results = await tester.run_performance_tests()
        report = tester.generate_report(results)
        all_reports.append(report)
        
        print(f"Grade: {report['performance_grade']}")
        print(f"Average RPS: {report['overall_metrics']['average_rps']:.1f}")
        print(f"Error Rate: {report['overall_metrics']['overall_error_rate']:.1f}%")
    
    # Save comprehensive report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"performance_test_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump({
            "test_timestamp": datetime.now().isoformat(),
            "scenarios": all_reports,
            "summary": {
                "total_scenarios": len(test_scenarios),
                "overall_grade": max([r["performance_grade"] for r in all_reports], key=lambda x: x.split()[0]),
                "recommendations": list(set(sum([r["recommendations"] for r in all_reports], [])))
            }
        }, f, indent=2)
    
    print(f"\n📄 Performance report saved: {report_file}")
    print("🎉 Performance testing completed!")

if __name__ == "__main__":
    asyncio.run(main())