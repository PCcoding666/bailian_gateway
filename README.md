# Alibaba Cloud Bailian API Integration Platform

This project provides a unified API interface for Alibaba Cloud Bailian platform services, allowing users to interact with various AI models including Qwen and Wanx.

## Project Structure

- `backend/` - Backend API service implementation
- `frontend/` - Frontend web interface
- `docs/` - Documentation
  - `api_spec.md` - API interface specifications
  - `database_design.md` - Database model design
  - `system_architecture.md` - System architecture design
  - `security_auth_scheme.md` - Security authentication and authorization scheme
  - `ui_design/` - Frontend UI design specifications

## Getting Started

### Using Docker (Recommended)

1. Install Docker and Docker Compose
2. Run the entire application stack:
   ```bash
   docker-compose up --build
   ```
3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend

1. Navigate to the `backend` directory
2. Install dependencies
3. Set up database
4. Configure environment variables
5. Run the server

#### Frontend

1. Navigate to the `frontend` directory
2. Install dependencies
3. Configure environment variables
4. Run the development server

## Features

- User authentication and authorization
- Conversation history management
- Multi-model AI service integration
- API rate limiting and monitoring
- Responsive web interface

## Technology Stack

- Backend: Python, FastAPI, MySQL, Redis
- Frontend: React, Vite
- Authentication: JWT, RBAC
- Deployment: Docker, Docker Compose

## Testing

- Unit tests: pytest
- Integration tests: pytest
- End-to-end tests: Selenium
- Test records: JSON format in `test_records/` directory

### Running Tests

To run all tests and record results:

```bash
./run_tests.sh
```

Or run the test runner directly:

```bash
python tests/test_runner.py --all
```