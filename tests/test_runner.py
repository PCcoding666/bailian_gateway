#!/usr/bin/env python3
"""
Test Runner for Alibaba Cloud Bailian API Integration Platform
"""

import subprocess
import sys
import os
import argparse
import json
from datetime import datetime

def run_backend_tests():
    """Run backend tests"""
    print("Running backend tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "backend/tests", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running backend tests: {e}")
        return False

def run_frontend_tests():
    """Run frontend tests"""
    print("Running frontend tests...")
    try:
        result = subprocess.run([
            "npm", "test"
        ], capture_output=True, text=True, cwd=os.path.join(os.getcwd(), "frontend"))
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running frontend tests: {e}")
        return False

def run_smoke_tests():
    """Run smoke tests"""
    print("Running smoke tests...")
    try:
        result = subprocess.run([
            sys.executable, "tests/smoke_test.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running smoke tests: {e}")
        return False

def run_frontend_accessibility_test():
    """Run frontend accessibility test"""
    print("Running frontend accessibility test...")
    try:
        result = subprocess.run([
            sys.executable, "tests/frontend_test.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running frontend accessibility test: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    # For now, we'll just run backend tests as integration tests
    # In a real scenario, you would have separate integration tests
    return run_backend_tests()

def record_test_results(results):
    """Record test results to a file"""
    timestamp = datetime.now().isoformat()
    test_record = {
        "timestamp": timestamp,
        "results": results
    }
    
    # Create test_records directory if it doesn't exist
    records_dir = os.path.join(os.getcwd(), "test_records")
    if not os.path.exists(records_dir):
        os.makedirs(records_dir)
    
    # Write test record to file
    record_file = os.path.join(records_dir, f"test_record_{timestamp.replace(':', '-')}.json")
    with open(record_file, 'w') as f:
        json.dump(test_record, f, indent=2)
    
    print(f"Test results recorded to {record_file}")

def main():
    parser = argparse.ArgumentParser(description="Test Runner for Bailian Gateway")
    parser.add_argument("--backend", action="store_true", help="Run backend tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--frontend-accessibility", action="store_true", help="Run frontend accessibility test")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # If no specific tests are requested, run all by default
    if not (args.backend or args.frontend or args.integration or args.smoke or args.frontend_accessibility or args.all):
        args.all = True
    
    results = {
        "backend": None,
        "frontend": None,
        "integration": None,
        "smoke": None,
        "frontend_accessibility": None
    }
    
    # Run requested tests
    if args.backend or args.all:
        results["backend"] = run_backend_tests()
    
    if args.frontend or args.all:
        results["frontend"] = run_frontend_tests()
    
    if args.integration or args.all:
        results["integration"] = run_integration_tests()
    
    if args.smoke or args.all:
        results["smoke"] = run_smoke_tests()
    
    if args.frontend_accessibility or args.all:
        results["frontend_accessibility"] = run_frontend_accessibility_test()
    
    # Record test results
    record_test_results(results)
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    for test_type, result in results.items():
        if result is not None:
            status = "PASSED" if result else "FAILED"
            print(f"{test_type.capitalize()} tests: {status}")
    
    # Return exit code based on test results
    all_passed = all(result for result in results.values() if result is not None)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())