from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from models import User
from services.bailian_api_service import BailianAPIService
from config.database import get_db
from api.auth import get_current_user_from_token

# Pydantic models for request/response
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None

class ChatCompletionResponse(BaseModel):
    code: int = 200
    message: str = "Success"
    data: Optional[Dict[str, Any]] = None

class GenerationRequest(BaseModel):
    model: str
    prompt: str
    parameters: Optional[Dict[str, Any]] = None

class GenerationResponse(BaseModel):
    code: int = 200
    message: str = "Success"
    data: Optional[Dict[str, Any]] = None

# Router
router = APIRouter(prefix="/api/bailian", tags=["bailian"])

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: Request,
    chat_request: ChatCompletionRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Call Qwen model for chat completions"""
    bailian_service = BailianAPIService(db)
    
    # Get client IP and user agent
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    result = bailian_service.call_qwen_model(
        model_name=chat_request.model,
        messages=chat_request.messages,
        user_id=current_user.id,
        temperature=chat_request.temperature,
        max_tokens=chat_request.max_tokens,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return ChatCompletionResponse(
        code=200,
        message="Request successful",
        data=result["data"]
    )

@router.post("/generation", response_model=GenerationResponse)
async def generation(
    request: Request,
    gen_request: GenerationRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Call Wanx model for content generation"""
    bailian_service = BailianAPIService(db)
    
    # Get client IP and user agent
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    result = bailian_service.call_wanx_model(
        model_name=gen_request.model,
        prompt=gen_request.prompt,
        parameters=gen_request.parameters,
        user_id=current_user.id,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return GenerationResponse(
        code=200,
        message="Request successful",
        data=result["data"]
    )