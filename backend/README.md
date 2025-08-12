# Backend API for Alibaba Cloud Bailian Integration Platform

This directory contains the backend API implementation for the Alibaba Cloud Bailian Integration Platform.

## Project Structure

- `api/` - API route definitions
- `models/` - Database models and schemas
- `services/` - Business logic implementations
- `utils/` - Utility functions and helpers
- `config/` - Configuration files
- `tests/` - Unit and integration tests

## Getting Started

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- Redis 6+

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```bash
   # This will be handled automatically by SQLAlchemy for now
   ```

### Running the Application

1. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

### Running Tests

```bash
pytest tests/
```

## API Documentation

API documentation is available through Swagger UI when the server is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

For production deployment, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```