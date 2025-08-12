#!/usr/bin/env python3
"""
Test Record Viewer for Alibaba Cloud Bailian API Integration Platform
"""

import os
import json
import argparse
from datetime import datetime

def list_test_records():
    """List all test records"""
    records_dir = os.path.join(os.getcwd(), "test_records")
    if not os.path.exists(records_dir):
        print("No test records found.")
        return
    
    records = []
    for filename in os.listdir(records_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(records_dir, filename)
            with open(filepath, 'r') as f:
                record = json.load(f)
                record['filename'] = filename
                records.append(record)
    
    # Sort records by timestamp
    records.sort(key=lambda x: x['timestamp'], reverse=True)
    
    print("Test Records:")
    print("-" * 80)
    for record in records:
        timestamp = record['timestamp']
        results = record['results']
        
        print(f"Timestamp: {timestamp}")
        print(f"File: {record['filename']}")
        
        for test_type, result in results.items():
            if result is not None:
                status = "PASSED" if result else "FAILED"
                print(f"  {test_type.capitalize()} tests: {status}")
        
        print("-" * 80)

def view_test_record(filename):
    """View a specific test record"""
    records_dir = os.path.join(os.getcwd(), "test_records")
    filepath = os.path.join(records_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"Test record {filename} not found.")
        return
    
    with open(filepath, 'r') as f:
        record = json.load(f)
    
    print(f"Test Record: {filename}")
    print("=" * 80)
    print(f"Timestamp: {record['timestamp']}")
    print("\nResults:")
    
    results = record['results']
    for test_type, result in results.items():
        if result is not None:
            status = "PASSED" if result else "FAILED"
            print(f"  {test_type.capitalize()} tests: {status}")

def main():
    parser = argparse.ArgumentParser(description="Test Record Viewer for Bailian Gateway")
    parser.add_argument("--list", action="store_true", help="List all test records")
    parser.add_argument("--view", type=str, help="View a specific test record")
    
    args = parser.parse_args()
    
    if args.view:
        view_test_record(args.view)
    else:
        list_test_records()

if __name__ == "__main__":
    main()