from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from models import User, Conversation, Message
from services.conversation_service import ConversationService
from services.message_service import MessageService
from config.database import get_db
from api.auth import get_current_user_from_token

# Pydantic models for request/response
class ConversationCreate(BaseModel):
    title: Optional[str] = None
    model_name: str

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class MessageCreate(BaseModel):
    content: list

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    user_id: int
    role: str
    content_type: str
    content: list
    status: int
    created_at: str

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    model_name: str
    status: int
    created_at: str
    updated_at: str

class PaginationResponse(BaseModel):
    current_page: int
    per_page: int
    total: int
    total_pages: int

class ConversationsResponse(BaseModel):
    conversations: List[ConversationResponse]
    pagination: PaginationResponse

class MessagesResponse(BaseModel):
    messages: List[MessageResponse]
    pagination: PaginationResponse

class APIResponse(BaseModel):
    code: int = 200
    message: str = "Success"
    data: Optional[dict] = None

# Router
router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.post("/", response_model=APIResponse)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    conversation_service = ConversationService(db)
    conversation = conversation_service.create_conversation(
        user_id=current_user.id,
        model_name=conversation_data.model_name,
        title=conversation_data.title
    )
    
    return APIResponse(
        code=200,
        message="Creation successful",
        data=conversation.to_dict()
    )

@router.get("/", response_model=APIResponse)
def get_conversations(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    if limit > 100:
        limit = 100
    
    conversation_service = ConversationService(db)
    conversations = conversation_service.get_user_conversations(
        user_id=current_user.id,
        skip=(page - 1) * limit,
        limit=limit
    )
    
    total = len(conversations)
    
    return APIResponse(
        code=200,
        message="Retrieval successful",
        data={
            "conversations": [conv.to_dict() for conv in conversations],
            "pagination": {
                "current_page": page,
                "per_page": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
    )

@router.get("/{conversation_id}", response_model=APIResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get conversation details"""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return APIResponse(
        code=200,
        message="Retrieval successful",
        data=conversation.to_dict()
    )

@router.put("/{conversation_id}", response_model=APIResponse)
def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Update conversation"""
    conversation_service = ConversationService(db)
    conversation = conversation_service.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        title=conversation_data.title
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return APIResponse(
        code=200,
        message="Update successful",
        data=conversation.to_dict()
    )

@router.delete("/{conversation_id}", response_model=APIResponse)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Delete conversation"""
    conversation_service = ConversationService(db)
    success = conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return APIResponse(
        code=200,
        message="Deletion successful",
        data=None
    )

@router.post("/{conversation_id}/messages", response_model=APIResponse)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Create a new message in conversation"""
    # Verify conversation belongs to user
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    message_service = MessageService(db)
    message = message_service.create_message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        role="user",
        content=message_data.content
    )
    
    return APIResponse(
        code=200,
        message="Send successful",
        data=message.to_dict()
    )

@router.get("/{conversation_id}/messages", response_model=APIResponse)
def get_messages(
    conversation_id: int,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get conversation messages"""
    if limit > 100:
        limit = 100
    
    message_service = MessageService(db)
    messages = message_service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
        skip=(page - 1) * limit,
        limit=limit
    )
    
    total = len(messages)
    
    return APIResponse(
        code=200,
        message="Retrieval successful",
        data={
            "messages": [msg.to_dict() for msg in messages],
            "pagination": {
                "current_page": page,
                "per_page": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
    )