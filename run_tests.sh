#!/usr/bin/env bash
# 
# Script to run all tests and record results

echo "Running all tests for Bailian Gateway..."

# Create test_records directory if it doesn't exist
mkdir -p test_records

# Run all tests
python tests/test_runner.py --all

echo "Test run completed. Results recorded in test_records/"