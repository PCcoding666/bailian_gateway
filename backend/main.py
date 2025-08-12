from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from config.database import engine, Base, get_db
from api import auth, conversations, bailian
from models import User, Conversation, Message, APICall
import os

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Alibaba Cloud Bailian API Integration Platform",
    description="A unified API interface for Alibaba Cloud Bailian platform services",
    version="0.1.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(bailian.router)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to the Alibaba Cloud Bailian API Integration Platform"}

# Create initial admin user if it doesn't exist
@app.on_event("startup")
def create_initial_admin():
    """Create initial admin user on startup"""
    db = next(get_db())
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            nickname="Administrator"
        )
        admin_user.set_password("AdminPass123!")
        db.add(admin_user)
        db.commit()