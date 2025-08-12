# Test Suite for Alibaba Cloud Bailian API Integration Platform

This directory contains the test suite for the Bailian Gateway project.

## Test Structure

- `test_runner.py` - Main test runner script
- `view_records.py` - Test record viewer
- `test_config.ini` - Test configuration file
- `test_records/` - Directory containing test records

## Running Tests

### Run all tests:

```bash
python tests/test_runner.py --all
```

### Run specific test suites:

```bash
# Run backend tests only
python tests/test_runner.py --backend

# Run frontend tests only
python tests/test_runner.py --frontend

# Run integration tests only
python tests/test_runner.py --integration

# Run smoke tests only
python tests/test_runner.py --smoke

# Run frontend accessibility test only
python tests/test_runner.py --frontend-accessibility
```

### Run backend tests directly:

```bash
cd backend
pytest tests/
```

### Run frontend tests directly:

```bash
cd frontend
npm test
```

## Viewing Test Records

### List all test records:

```bash
python tests/view_records.py --list
```

### View a specific test record:

```bash
python tests/view_records.py --view test_record_2023-01-01T10-00-00.json
```

## Test Configuration

The `test_config.ini` file contains configuration settings for the tests, including:

- Base URLs for backend and frontend services
- Test database configuration
- Test user credentials

## Test Records

Test results are automatically recorded in JSON format in the `test_records/` directory. Each record contains:

- Timestamp of the test run
- Results for each test suite (passed/failed)