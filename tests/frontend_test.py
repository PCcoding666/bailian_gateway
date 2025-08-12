#!/usr/bin/env python3
"""
Simple test to verify the frontend is working
"""

import requests
import sys
import os

def test_frontend():
    """Test frontend"""
    base_url = "http://localhost:3000"
    
    print("Testing frontend...")
    
    # Test if frontend is accessible
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✓ Frontend is accessible")
        else:
            print("✗ Frontend is not accessible")
            return False
    except Exception as e:
        print(f"✗ Frontend is not accessible: {e}")
        return False
    
    print("Frontend test passed!")
    return True

def main():
    if test_frontend():
        print("\nFrontend is working correctly.")
        return 0
    else:
        print("\nFrontend tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())