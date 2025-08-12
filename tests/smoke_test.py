#!/usr/bin/env python3
"""
Simple test to verify the backend API is working
"""

import requests
import sys
import os

def test_backend_api():
    """Test backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing backend API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("✓ Health check passed")
        else:
            print("✗ Health check failed")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Root endpoint passed")
        else:
            print("✗ Root endpoint failed")
            return False
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
        return False
    
    # Test auth endpoints (should return 401 without auth)
    try:
        response = requests.get(f"{base_url}/api/auth/user")
        if response.status_code == 401:
            print("✓ Auth endpoint correctly requires authentication")
        else:
            print("✗ Auth endpoint should require authentication")
            return False
    except Exception as e:
        print(f"✗ Auth endpoint test failed: {e}")
        return False
    
    print("All backend API tests passed!")
    return True

def main():
    if test_backend_api():
        print("\nBackend API is working correctly.")
        return 0
    else:
        print("\nBackend API tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())