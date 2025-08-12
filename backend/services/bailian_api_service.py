import os
from typing import List, Dict, Any
from openai import OpenAI
from dashscope import Generation
import dashscope
from services.api_call_service import APICallService
from sqlalchemy.orm import Session
import time
import json

class BailianAPIService:
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

    def call_qwen_model(self, model_name: str, messages: List[Dict[str, Any]], 
                       user_id: int, conversation_id: int = None, 
                       temperature: float = 1.0, max_tokens: int = None,
                       client_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Call Qwen model through OpenAI-compatible API"""
        start_time = time.time()
        
        try:
            # Prepare request
            request_data = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                request_data["max_tokens"] = max_tokens
            
            # Make API call
            response = self.openai_client.chat.completions.create(**request_data)
            
            # Calculate duration
            call_duration = int((time.time() - start_time) * 1000)
            
            # Extract token usage
            usage = response.usage if hasattr(response, 'usage') else None
            request_tokens = usage.prompt_tokens if usage else 0
            response_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0
            
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
            
            return {
                "success": True,
                "data": response.model_dump() if hasattr(response, 'model_dump') else response.dict(),
                "usage": {
                    "request_tokens": request_tokens,
                    "response_tokens": response_tokens,
                    "total_tokens": total_tokens,
                    "call_duration": call_duration
                }
            }
            
        except Exception as e:
            # Calculate duration
            call_duration = int((time.time() - start_time) * 1000)
            
            # Log failed API call
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
            
            return {
                "success": False,
                "error": str(e),
                "usage": {
                    "call_duration": call_duration
                }
            }

    def call_wanx_model(self, model_name: str, prompt: str, parameters: Dict[str, Any] = None,
                       user_id: int, client_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Call Wanx model through DashScope API"""
        start_time = time.time()
        
        try:
            # Prepare request
            request_data = {
                "model": model_name,
                "prompt": prompt
            }
            
            if parameters:
                request_data.update(parameters)
            
            # Make API call
            response = Generation.call(**request_data)
            
            # Calculate duration
            call_duration = int((time.time() - start_time) * 1000)
            
            # Extract usage information
            usage = response.usage if hasattr(response, 'usage') else None
            request_tokens = usage.input_tokens if usage and hasattr(usage, 'input_tokens') else 0
            response_tokens = usage.output_tokens if usage and hasattr(usage, 'output_tokens') else 0
            total_tokens = request_tokens + response_tokens
            
            # Log API call
            self.api_call_service.log_api_call(
                user_id=user_id,
                api_endpoint="/api/bailian/generation",
                model_name=model_name,
                request_content=request_data,
                response_content=response.__dict__ if hasattr(response, '__dict__') else str(response),
                status_code=200,
                request_tokens=request_tokens,
                response_tokens=response_tokens,
                total_tokens=total_tokens,
                call_duration=call_duration,
                client_ip=client_ip,
                user_agent=user_agent
            )
            
            return {
                "success": True,
                "data": response.__dict__ if hasattr(response, '__dict__') else str(response),
                "usage": {
                    "request_tokens": request_tokens,
                    "response_tokens": response_tokens,
                    "total_tokens": total_tokens,
                    "call_duration": call_duration
                }
            }
            
        except Exception as e:
            # Calculate duration
            call_duration = int((time.time() - start_time) * 1000)
            
            # Log failed API call
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
            
            return {
                "success": False,
                "error": str(e),
                "usage": {
                    "call_duration": call_duration
                }
            }