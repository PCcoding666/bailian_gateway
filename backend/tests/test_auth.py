import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base
from main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override database dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_register_user():
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]

def test_login_user():
    # First register a user
    client.post("/api/auth/register", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "TestPass123!"
    })
    
    # Then login
    response = client.post("/api/auth/login", json={
        "username": "testuser2",
        "password": "TestPass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]