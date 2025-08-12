# Claude Code Configuration for Bailian Gateway

This file contains project-specific information that Claude Code should remember when working on this repository.

## Project Overview
This is the Alibaba Cloud Bailian API Integration Platform, providing a unified interface for Alibaba Cloud Bailian services.

## Common Bash Commands
- `cd backend` - Navigate to backend directory
- `cd frontend` - Navigate to frontend directory
- `pip install -r requirements.txt` - Install backend dependencies
- `npm install` - Install frontend dependencies
- `npm run dev` - Start frontend development server
- `uvicorn main:app --reload` - Start backend development server

## Core Files and Utility Functions
- Backend entry point: `backend/main.py`
- Database models: `backend/models/`
- API routes: `backend/api/`
- Configuration: `backend/config/`
- Services: `backend/services/`

## Code Style Guidelines
- Backend: Python with FastAPI, following PEP 8
- Frontend: React with functional components and hooks
- Database: SQLAlchemy ORM
- Security: JWT for authentication, bcrypt for password hashing

## Testing Instructions
- Backend tests: `pytest backend/tests/`
- Frontend tests: `npm test`

## Repository Etiquette
- Branch naming: feature/your-feature-name or bugfix/issue-description
- Commits: Clear, concise messages in present tense
- Pull requests: Include description of changes and testing steps

## Developer Environment Setup
- Python 3.9+
- Node.js 16+
- MySQL 8.0+
- Redis 6+

## Project Structure
- `backend/` - Python FastAPI application
- `frontend/` - React application
- `docs/` - Documentation files
- `docs/progress/` - Implementation progress tracking

## Key Implementation Notes
- Follow the database schema defined in docs/database_design.md
- Implement JWT-based authentication as specified in docs/security_auth_scheme.md
- Use the API specifications in docs/api_spec.md for endpoint design
- Follow the UI design guidelines in docs/ui_design/frontend_ui_design.md

## Progress Tracking
Implementation progress is tracked in docs/progress/mvp_progress.md