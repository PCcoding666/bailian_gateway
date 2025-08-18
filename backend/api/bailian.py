from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from models import User
from services.enhanced_bailian_service import EnhancedBailianAPIService, SupportedModels
from config.database import get_db
from api.auth import get_current_user_from_token

# Pydantic models for request/response
class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="AI model name (qwen-max, qwen-vl-max)")
    messages: List[Dict[str, Any]] = Field(..., description="Chat conversation messages")
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0, description="Randomness control")
    max_tokens: Optional[int] = Field(default=None, gt=0, description="Maximum response tokens")
    conversation_id: Optional[int] = Field(default=None, description="Conversation ID for tracking")

class ChatCompletionResponse(BaseModel):
    code: int = 200
    message: str = "Success"
    data: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None

class MultimodalRequest(BaseModel):
    model: str = Field(default=SupportedModels.QWEN_VL_MAX.value, description="Multimodal model name")
    messages: List[Dict[str, Any]] = Field(..., description="Messages with text and image content")
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    conversation_id: Optional[int] = Field(default=None)

class GenerationRequest(BaseModel):
    model: str = Field(default=SupportedModels.WAN2_T2I_PLUS.value, description="Image generation model")
    prompt: str = Field(..., min_length=1, max_length=2000, description="Generation prompt")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Model-specific parameters")

class GenerationResponse(BaseModel):
    code: int = 200
    message: str = "Success"
    data: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None

class ModelStatusResponse(BaseModel):
    supported_models: List[str]
    model_capabilities: Dict[str, Any]
    api_key_configured: bool
    service_status: str

# Router
router = APIRouter(prefix="/api/bailian", tags=["bailian"])

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: Request,
    chat_request: ChatCompletionRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Call Qwen models for chat completions (qwen-max, qwen-vl-max)"""
    bailian_service = EnhancedBailianAPIService(db)
    
    # Validate model
    if chat_request.model not in [SupportedModels.QWEN_MAX.value, SupportedModels.QWEN_VL_MAX.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model for chat completions: {chat_request.model}. Use qwen-max or qwen-vl-max"
        )
    
    # Get client information
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Route to appropriate model handler
    if chat_request.model == SupportedModels.QWEN_MAX.value:
        result = bailian_service.call_qwen_max(
            messages=chat_request.messages,
            user_id=current_user.id,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            conversation_id=chat_request.conversation_id,
            client_ip=client_ip,
            user_agent=user_agent
        )
    else:  # qwen-vl-max
        result = bailian_service.call_qwen_vl_max(
            messages=chat_request.messages,
            user_id=current_user.id,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            conversation_id=chat_request.conversation_id,
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
        data=result["data"],
        usage=result.get("usage")
    )

@router.post("/generation", response_model=GenerationResponse)
async def generation(
    request: Request,
    gen_request: GenerationRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Call Wan2.2-T2I-Plus model for high-quality image generation"""
    bailian_service = EnhancedBailianAPIService(db)
    
    # Validate model
    if gen_request.model != SupportedModels.WAN2_T2I_PLUS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model for generation: {gen_request.model}. Use wan2.2-t2i-plus"
        )
    
    # Get client information
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    result = bailian_service.call_wan2_t2i_plus(
        prompt=gen_request.prompt,
        user_id=current_user.id,
        parameters=gen_request.parameters,
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
        data=result["data"],
        usage=result.get("usage")
    )

@router.post("/multimodal", response_model=ChatCompletionResponse)
async def multimodal_chat(
    request: Request,
    multimodal_request: MultimodalRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Call Qwen-VL-Max for multimodal conversations (text + vision)"""
    bailian_service = EnhancedBailianAPIService(db)
    
    # Get client information
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    result = bailian_service.call_qwen_vl_max(
        messages=multimodal_request.messages,
        user_id=current_user.id,
        temperature=multimodal_request.temperature,
        max_tokens=multimodal_request.max_tokens,
        conversation_id=multimodal_request.conversation_id,
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
        message="Multimodal request successful",
        data=result["data"],
        usage=result.get("usage")
    )

@router.get("/models/status", response_model=ModelStatusResponse)
async def get_model_status(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get status and capabilities of all supported models"""
    bailian_service = EnhancedBailianAPIService(db)
    status_info = bailian_service.get_model_status()
    
    return ModelStatusResponse(**status_info)

@router.get("/models/supported")
async def list_supported_models(
    current_user: User = Depends(get_current_user_from_token)
):
    """List all supported models with their use cases"""
    return {
        "code": 200,
        "message": "Supported models retrieved successfully",
        "data": {
            "models": [
                {
                    "name": SupportedModels.QWEN_MAX.value,
                    "description": "Advanced reasoning and complex task completion",
                    "capabilities": ["text-generation", "reasoning", "analysis"],
                    "endpoint": "/api/bailian/chat/completions",
                    "max_tokens": 8192
                },
                {
                    "name": SupportedModels.QWEN_VL_MAX.value,
                    "description": "Multimodal understanding with vision capabilities",
                    "capabilities": ["text-generation", "image-understanding", "multimodal"],
                    "endpoint": "/api/bailian/multimodal",
                    "max_tokens": 8192
                },
                {
                    "name": SupportedModels.WAN2_T2I_PLUS.value,
                    "description": "High-quality text-to-image generation",
                    "capabilities": ["image-generation", "artistic-creation"],
                    "endpoint": "/api/bailian/generation",
                    "output_format": "image_url"
                }
            ]
        }
    }