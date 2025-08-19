"""
Enhanced Bailian API Service with Support for Specific Qwen Models
Supports: qwen-max, qwen-vl-max, wan2.2-t2i-plus
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session

# External dependencies
from openai import OpenAI
import dashscope
from dashscope import Generation, MultiModalConversation

# Internal dependencies
from services.api_call_service import APICallService
from utils.cloud_logger import cloud_logger
from utils.metrics import record_ai_request, record_token_usage

# Configure logger
logger = cloud_logger

class SupportedModels(Enum):
    """Supported Qwen and Wanx models"""
    QWEN_MAX = "qwen-max"
    QWEN_VL_MAX = "qwen-vl-max"  
    WAN2_T2I_PLUS = "wan2.2-t2i-plus"

@dataclass
class ModelCapabilities:
    """Model capabilities and limitations"""
    model_name: str
    max_tokens: int
    supports_multimodal: bool
    supports_image_generation: bool
    rate_limit_rpm: int  # requests per minute
    cost_per_token: float

class ModelRegistry:
    """Registry of supported models and their capabilities"""
    
    MODELS = {
        SupportedModels.QWEN_MAX.value: ModelCapabilities(
            model_name="qwen-max",
            max_tokens=8192,
            supports_multimodal=False,
            supports_image_generation=False,
            rate_limit_rpm=100,
            cost_per_token=0.002
        ),
        SupportedModels.QWEN_VL_MAX.value: ModelCapabilities(
            model_name="qwen-vl-max",
            max_tokens=8192,
            supports_multimodal=True,
            supports_image_generation=False,
            rate_limit_rpm=60,
            cost_per_token=0.003
        ),
        SupportedModels.WAN2_T2I_PLUS.value: ModelCapabilities(
            model_name="wan2.2-t2i-plus",
            max_tokens=1024,
            supports_multimodal=False,
            supports_image_generation=True,
            rate_limit_rpm=20,
            cost_per_token=0.01
        )
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[ModelCapabilities]:
        """Get model capabilities"""
        return cls.MODELS.get(model_name)
    
    @classmethod
    def is_supported(cls, model_name: str) -> bool:
        """Check if model is supported"""
        return model_name in cls.MODELS
    
    @classmethod
    def list_supported_models(cls) -> List[str]:
        """List all supported models"""
        return list(cls.MODELS.keys())

class EnhancedBailianAPIService:
    """Enhanced Bailian API Service with comprehensive model support"""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_call_service = APICallService(db)
        
        # Initialize OpenAI client for Qwen models
        self.openai_client = OpenAI(
            api_key=os.getenv("QWEN_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        # Initialize DashScope client
        dashscope.api_key = os.getenv("QWEN_API_KEY")
        
        # Model registry
        self.model_registry = ModelRegistry()
        
        logger.info(f"Enhanced Bailian service initialized with models: {self.model_registry.list_supported_models()}")
    
    def validate_model_request(self, model_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model request against capabilities"""
        model_info = self.model_registry.get_model_info(model_name)
        
        if not model_info:
            return {
                "valid": False,
                "error": f"Unsupported model: {model_name}. Supported models: {self.model_registry.list_supported_models()}"
            }
        
        # Check token limits
        if "max_tokens" in request_data:
            if request_data["max_tokens"] > model_info.max_tokens:
                return {
                    "valid": False,
                    "error": f"max_tokens {request_data['max_tokens']} exceeds model limit {model_info.max_tokens}"
                }
        
        # Check multimodal support
        if "messages" in request_data:
            for message in request_data["messages"]:
                if isinstance(message.get("content"), list) and not model_info.supports_multimodal:
                    return {
                        "valid": False,
                        "error": f"Model {model_name} does not support multimodal content"
                    }
        
        return {"valid": True, "model_info": model_info}

    def call_qwen_max(self, messages: List[Dict[str, Any]], user_id: int, 
                     temperature: float = 1.0, max_tokens: int = None,
                     conversation_id: int = None, client_ip: str = None, 
                     user_agent: str = None) -> Dict[str, Any]:
        """Call Qwen-Max model for advanced reasoning tasks"""
        model_name = SupportedModels.QWEN_MAX.value
        start_time = time.time()
        
        try:
            # Validate request
            validation = self.validate_model_request(model_name, {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            })
            
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}
            
            # Prepare request
            request_data = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                request_data["max_tokens"] = min(max_tokens, validation["model_info"].max_tokens)
            
            logger.info(f"Calling Qwen-Max with {len(messages)} messages", extra={
                "user_id": user_id,
                "model": model_name,
                "temperature": temperature
            })
            
            # Make API call
            response = self.openai_client.chat.completions.create(**request_data)
            
            # Calculate metrics
            call_duration = int((time.time() - start_time) * 1000)
            usage = response.usage if hasattr(response, 'usage') else None
            request_tokens = usage.prompt_tokens if usage else 0
            response_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0
            
            # Record metrics
            record_ai_request(model_name, "success", call_duration)
            record_token_usage(model_name, "input", request_tokens)
            record_token_usage(model_name, "output", response_tokens)
            
            # Log API call
            self.api_call_service.log_api_call(
                user_id=user_id,
                api_endpoint="/api/bailian/chat/completions",
                model_name=model_name,
                request_content=request_data,
                response_content=response.model_dump() if hasattr(response, 'model_dump') else response.dict(),
                status_code=200,
                request_tokens=request_tokens,
                response_tokens=response_tokens,
                total_tokens=total_tokens,
                call_duration=call_duration,
                client_ip=client_ip,
                user_agent=user_agent,
                conversation_id=conversation_id
            )
            
            logger.info(f"Qwen-Max call successful", extra={
                "user_id": user_id,
                "tokens_used": total_tokens,
                "duration_ms": call_duration
            })
            
            return {
                "success": True,
                "data": response.model_dump() if hasattr(response, 'model_dump') else response.dict(),
                "usage": {
                    "request_tokens": request_tokens,
                    "response_tokens": response_tokens,
                    "total_tokens": total_tokens,
                    "call_duration": call_duration,
                    "estimated_cost": total_tokens * validation["model_info"].cost_per_token
                }
            }
            
        except Exception as e:
            call_duration = int((time.time() - start_time) * 1000)
            
            # Record error metrics
            record_ai_request(model_name, "error", call_duration)
            
            # Log failed call
            self.api_call_service.log_api_call(
                user_id=user_id,
                api_endpoint="/api/bailian/chat/completions",
                model_name=model_name,
                request_content={"model": model_name, "messages": messages},
                response_content={"error": str(e)},
                status_code=500,
                call_duration=call_duration,
                client_ip=client_ip,
                user_agent=user_agent,
                conversation_id=conversation_id
            )
            
            logger.error(f"Qwen-Max call failed: {str(e)}", extra={
                "user_id": user_id,
                "model": model_name,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e),
                "usage": {"call_duration": call_duration}
            }

    def call_qwen_vl_max(self, messages: List[Dict[str, Any]], user_id: int,
                        temperature: float = 1.0, max_tokens: int = None,
                        conversation_id: int = None, client_ip: str = None,
                        user_agent: str = None) -> Dict[str, Any]:
        """Call Qwen-VL-Max model for multimodal tasks (text + vision)"""
        model_name = SupportedModels.QWEN_VL_MAX.value
        start_time = time.time()
        
        try:
            # Validate request
            validation = self.validate_model_request(model_name, {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            })
            
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}
            
            logger.info(f"Calling Qwen-VL-Max with {len(messages)} messages", extra={
                "user_id": user_id,
                "model": model_name,
                "has_multimodal": any(isinstance(msg.get("content"), list) for msg in messages)
            })
            
            # Use DashScope MultiModalConversation for vision tasks
            response = MultiModalConversation.call(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or validation["model_info"].max_tokens
            )
            
            # Calculate metrics
            call_duration = int((time.time() - start_time) * 1000)
            usage = response.usage if hasattr(response, 'usage') else None
            request_tokens = usage.input_tokens if usage and hasattr(usage, 'input_tokens') else 0
            response_tokens = usage.output_tokens if usage and hasattr(usage, 'output_tokens') else 0
            total_tokens = request_tokens + response_tokens
            
            # Record metrics
            record_ai_request(model_name, "success", call_duration)
            record_token_usage(model_name, "input", request_tokens)
            record_token_usage(model_name, "output", response_tokens)
            
            # Log API call
            self.api_call_service.log_api_call(
                user_id=user_id,
                api_endpoint="/api/bailian/multimodal",
                model_name=model_name,
                request_content={"model": model_name, "messages": messages},
                response_content=response.__dict__ if hasattr(response, '__dict__') else str(response),
                status_code=200,
                request_tokens=request_tokens,
                response_tokens=response_tokens,
                total_tokens=total_tokens,
                call_duration=call_duration,
                client_ip=client_ip,
                user_agent=user_agent,
                conversation_id=conversation_id
            )
            
            logger.info(f"Qwen-VL-Max call successful", extra={
                "user_id": user_id,
                "tokens_used": total_tokens,
                "duration_ms": call_duration
            })
            
            return {
                "success": True,
                "data": response.__dict__ if hasattr(response, '__dict__') else str(response),
                "usage": {
                    "request_tokens": request_tokens,
                    "response_tokens": response_tokens,
                    "total_tokens": total_tokens,
                    "call_duration": call_duration,
                    "estimated_cost": total_tokens * validation["model_info"].cost_per_token
                }
            }
            
        except Exception as e:
            call_duration = int((time.time() - start_time) * 1000)
            
            # Record error metrics
            record_ai_request(model_name, "error", call_duration)
            
            # Log failed call
            self.api_call_service.log_api_call(
                user_id=user_id,
                api_endpoint="/api/bailian/multimodal",
                model_name=model_name,
                request_content={"model": model_name, "messages": messages},
                response_content={"error": str(e)},
                status_code=500,
                call_duration=call_duration,
                client_ip=client_ip,
                user_agent=user_agent,
                conversation_id=conversation_id
            )
            
            logger.error(f"Qwen-VL-Max call failed: {str(e)}", extra={
                "user_id": user_id,
                "model": model_name,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e),
                "usage": {"call_duration": call_duration}
            }

    def call_wan2_t2i_plus(self, prompt: str, user_id: int, 
                          parameters: Dict[str, Any] = None,
                          client_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Call Wan2.2-T2I-Plus model for high-quality image generation"""
        model_name = SupportedModels.WAN2_T2I_PLUS.value
        start_time = time.time()
        
        try:
            # Validate request
            validation = self.validate_model_request(model_name, {
                "prompt": prompt,
                "parameters": parameters or {}
            })
            
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}
            
            # Prepare request with optimized parameters for wan2.2-t2i-plus
            request_data = {
                "model": model_name,
                "prompt": prompt,
                "parameters": {
                    "size": "1024*1024",  # Default high resolution
                    "quality": "high",
                    "style": "realistic",
                    **(parameters or {})
                }
            }
            
            logger.info(f"Calling Wan2.2-T2I-Plus for image generation", extra={
                "user_id": user_id,
                "model": model_name,
                "prompt_length": len(prompt)
            })
            
            # Make API call using DashScope Generation
            response = Generation.call(**request_data)
            
            # Calculate metrics
            call_duration = int((time.time() - start_time) * 1000)
            
            # For image generation, we estimate token usage based on prompt
            estimated_tokens = len(prompt.split())
            
            # Record metrics
            record_ai_request(model_name, "success", call_duration)
            record_token_usage(model_name, "input", estimated_tokens)
            
            # Log API call
            self.api_call_service.log_api_call(
                user_id=user_id,
                api_endpoint="/api/bailian/generation",
                model_name=model_name,
                request_content=request_data,
                response_content=response.__dict__ if hasattr(response, '__dict__') else str(response),
                status_code=200,
                request_tokens=estimated_tokens,
                response_tokens=0,  # Image generation doesn't have response tokens
                total_tokens=estimated_tokens,
                call_duration=call_duration,
                client_ip=client_ip,
                user_agent=user_agent
            )
            
            logger.info(f"Wan2.2-T2I-Plus call successful", extra={
                "user_id": user_id,
                "duration_ms": call_duration,
                "has_results": hasattr(response, 'output') and response.output
            })
            
            return {
                "success": True,
                "data": response.__dict__ if hasattr(response, '__dict__') else str(response),
                "usage": {
                    "request_tokens": estimated_tokens,
                    "response_tokens": 0,
                    "total_tokens": estimated_tokens,
                    "call_duration": call_duration,
                    "estimated_cost": validation["model_info"].cost_per_token  # Flat rate for image generation
                }
            }
            
        except Exception as e:
            call_duration = int((time.time() - start_time) * 1000)
            
            # Record error metrics
            record_ai_request(model_name, "error", call_duration)
            
            # Log failed call
            self.api_call_service.log_api_call(
                user_id=user_id,
                api_endpoint="/api/bailian/generation",
                model_name=model_name,
                request_content={"model": model_name, "prompt": prompt},
                response_content={"error": str(e)},
                status_code=500,
                call_duration=call_duration,
                client_ip=client_ip,
                user_agent=user_agent
            )
            
            logger.error(f"Wan2.2-T2I-Plus call failed: {str(e)}", extra={
                "user_id": user_id,
                "model": model_name,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e),
                "usage": {"call_duration": call_duration}
            }

    def route_model_request(self, model_name: str, request_type: str, **kwargs) -> Dict[str, Any]:
        """Route requests to appropriate model handlers"""
        if not self.model_registry.is_supported(model_name):
            return {
                "success": False,
                "error": f"Unsupported model: {model_name}. Supported models: {self.model_registry.list_supported_models()}"
            }
        
        try:
            if model_name == SupportedModels.QWEN_MAX.value:
                if request_type == "chat":
                    return self.call_qwen_max(**kwargs)
                    
            elif model_name == SupportedModels.QWEN_VL_MAX.value:
                if request_type == "chat" or request_type == "multimodal":
                    return self.call_qwen_vl_max(**kwargs)
                    
            elif model_name == SupportedModels.WAN2_T2I_PLUS.value:
                if request_type == "generation" or request_type == "image":
                    return self.call_wan2_t2i_plus(**kwargs)
            
            return {
                "success": False,
                "error": f"Request type '{request_type}' not supported for model '{model_name}'"
            }
            
        except Exception as e:
            logger.error(f"Model routing failed: {str(e)}", extra={
                "model": model_name,
                "request_type": request_type,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": f"Model routing error: {str(e)}"
            }

    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all supported models"""
        return {
            "supported_models": self.model_registry.list_supported_models(),
            "model_capabilities": {
                model_name: {
                    "max_tokens": info.max_tokens,
                    "supports_multimodal": info.supports_multimodal,
                    "supports_image_generation": info.supports_image_generation,
                    "rate_limit_rpm": info.rate_limit_rpm,
                    "cost_per_token": info.cost_per_token
                }
                for model_name, info in self.model_registry.MODELS.items()
            },
            "api_key_configured": bool(os.getenv("QWEN_API_KEY")),
            "service_status": "ready"
        }