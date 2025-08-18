"""
Function Compute Service for Serverless AI Processing
Handles AI model inference with automatic scaling and cost optimization
"""

import json
import os
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import httpx
from utils.cloud_logger import cloud_logger
from utils.metrics import metrics
from config.cloud_config import get_ai_service_config

@dataclass
class FunctionComputeRequest:
    """Function Compute request structure"""
    model: str
    prompt: str
    messages: Optional[List[Dict[str, Any]]] = None
    parameters: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    correlation_id: Optional[str] = None

@dataclass
class FunctionComputeResponse:
    """Function Compute response structure"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0
    token_usage: Optional[Dict[str, int]] = None

class FunctionComputeService:
    """Service for integrating with Alibaba Cloud Function Compute"""
    
    def __init__(self):
        self.config = get_ai_service_config()
        self.function_endpoints = {
            'qwen': os.getenv('FC_QWEN_ENDPOINT', ''),
            'wanx': os.getenv('FC_WANX_ENDPOINT', ''),
            'text_processing': os.getenv('FC_TEXT_PROCESSING_ENDPOINT', ''),
            'image_generation': os.getenv('FC_IMAGE_GEN_ENDPOINT', '')
        }
        
        # HTTP client for Function Compute calls
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def invoke_qwen_function(self, request: FunctionComputeRequest) -> FunctionComputeResponse:
        """Invoke Qwen model processing function"""
        return await self._invoke_function('qwen', request)
    
    async def invoke_wanx_function(self, request: FunctionComputeRequest) -> FunctionComputeResponse:
        """Invoke Wanx model processing function"""
        return await self._invoke_function('wanx', request)
    
    async def invoke_text_processing_function(self, request: FunctionComputeRequest) -> FunctionComputeResponse:
        """Invoke text processing function"""
        return await self._invoke_function('text_processing', request)
    
    async def invoke_image_generation_function(self, request: FunctionComputeRequest) -> FunctionComputeResponse:
        """Invoke image generation function"""
        return await self._invoke_function('image_generation', request)
    
    async def _invoke_function(self, function_name: str, request: FunctionComputeRequest) -> FunctionComputeResponse:
        """Generic function invocation"""
        start_time = datetime.utcnow()
        
        try:
            endpoint = self.function_endpoints.get(function_name)
            if not endpoint:
                error_msg = f"No endpoint configured for function: {function_name}"
                cloud_logger.error(error_msg, function_name=function_name)
                return FunctionComputeResponse(success=False, error=error_msg)
            
            # Prepare request payload
            payload = {
                'model': request.model,
                'prompt': request.prompt,
                'messages': request.messages,
                'parameters': request.parameters or {},
                'user_id': request.user_id,
                'correlation_id': request.correlation_id
            }
            
            # Log function invocation
            cloud_logger.info(
                f"Invoking Function Compute: {function_name}",
                function_name=function_name,
                model=request.model,
                user_id=request.user_id,
                correlation_id=request.correlation_id
            )
            
            # Make HTTP request to Function Compute
            response = await self.http_client.post(
                endpoint,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Correlation-ID': request.correlation_id or '',
                    'Authorization': f'Bearer {os.getenv("FC_AUTH_TOKEN", "")}'
                }
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Extract token usage if available
                token_usage = result_data.get('token_usage', {})
                
                # Log successful invocation
                cloud_logger.info(
                    f"Function Compute invocation successful: {function_name}",
                    function_name=function_name,
                    execution_time_ms=execution_time,
                    token_usage=token_usage,
                    correlation_id=request.correlation_id
                )
                
                # Record metrics
                metrics.record_ai_request(
                    model=request.model,
                    status='success',
                    duration=execution_time / 1000,
                    input_tokens=token_usage.get('input_tokens', 0),
                    output_tokens=token_usage.get('output_tokens', 0)
                )
                
                return FunctionComputeResponse(
                    success=True,
                    data=result_data,
                    execution_time_ms=execution_time,
                    token_usage=token_usage
                )
            else:
                error_msg = f"Function Compute returned {response.status_code}: {response.text}"
                cloud_logger.error(
                    f"Function Compute invocation failed: {function_name}",
                    function_name=function_name,
                    status_code=response.status_code,
                    error=error_msg,
                    execution_time_ms=execution_time,
                    correlation_id=request.correlation_id
                )
                
                # Record metrics
                metrics.record_ai_request(
                    model=request.model,
                    status='error',
                    duration=execution_time / 1000
                )
                
                return FunctionComputeResponse(
                    success=False,
                    error=error_msg,
                    execution_time_ms=execution_time
                )
                
        except httpx.TimeoutException:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            error_msg = f"Function Compute timeout: {function_name}"
            cloud_logger.error(error_msg, function_name=function_name, execution_time_ms=execution_time)
            
            metrics.record_ai_request(
                model=request.model,
                status='timeout',
                duration=execution_time / 1000
            )
            
            return FunctionComputeResponse(
                success=False,
                error=error_msg,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            error_msg = f"Function Compute invocation error: {str(e)}"
            cloud_logger.error(
                error_msg,
                function_name=function_name,
                error_type=type(e).__name__,
                execution_time_ms=execution_time,
                correlation_id=request.correlation_id
            )
            
            metrics.record_ai_request(
                model=request.model,
                status='error',
                duration=execution_time / 1000
            )
            
            return FunctionComputeResponse(
                success=False,
                error=error_msg,
                execution_time_ms=execution_time
            )
    
    async def batch_invoke(self, requests: List[FunctionComputeRequest], function_name: str) -> List[FunctionComputeResponse]:
        """Batch invoke functions for better performance"""
        tasks = [self._invoke_function(function_name, request) for request in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all configured Function Compute endpoints"""
        health_status = {}
        
        for function_name, endpoint in self.function_endpoints.items():
            if not endpoint:
                health_status[function_name] = False
                continue
                
            try:
                # Simple health check request
                response = await self.http_client.get(
                    f"{endpoint}/health",
                    timeout=5.0
                )
                health_status[function_name] = response.status_code == 200
            except Exception:
                health_status[function_name] = False
        
        return health_status
    
    async def close(self):
        """Clean up HTTP client"""
        await self.http_client.aclose()

# Function Compute function templates for deployment

QWEN_FUNCTION_TEMPLATE = '''
import json
import os
from dashscope import Generation

def handler(event, context):
    """
    Qwen model processing function for Function Compute
    """
    try:
        # Parse request body
        if isinstance(event, str):
            request_data = json.loads(event)
        else:
            request_data = json.loads(event.get('body', '{}'))
        
        # Extract parameters
        model = request_data.get('model', 'qwen-max')
        messages = request_data.get('messages', [])
        prompt = request_data.get('prompt', '')
        parameters = request_data.get('parameters', {})
        correlation_id = request_data.get('correlation_id', '')
        
        # Prepare messages for Qwen
        if prompt and not messages:
            messages = [{"role": "user", "content": prompt}]
        
        # Call Qwen API
        response = Generation.call(
            model=model,
            messages=messages,
            api_key=os.environ.get('DASHSCOPE_API_KEY'),
            **parameters
        )
        
        if response.status_code == 200:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'X-Correlation-ID': correlation_id
                },
                'body': json.dumps({
                    'success': True,
                    'data': response.output,
                    'token_usage': {
                        'input_tokens': response.usage.get('input_tokens', 0),
                        'output_tokens': response.usage.get('output_tokens', 0),
                        'total_tokens': response.usage.get('total_tokens', 0)
                    }
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': f'Qwen API error: {response.message}'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
'''

WANX_FUNCTION_TEMPLATE = '''
import json
import os
from dashscope import ImageSynthesis

def handler(event, context):
    """
    Wanx image generation function for Function Compute
    """
    try:
        # Parse request body
        if isinstance(event, str):
            request_data = json.loads(event)
        else:
            request_data = json.loads(event.get('body', '{}'))
        
        # Extract parameters
        model = request_data.get('model', 'wanx-v1')
        prompt = request_data.get('prompt', '')
        parameters = request_data.get('parameters', {})
        correlation_id = request_data.get('correlation_id', '')
        
        # Call Wanx API
        response = ImageSynthesis.call(
            model=model,
            prompt=prompt,
            api_key=os.environ.get('DASHSCOPE_API_KEY'),
            **parameters
        )
        
        if response.status_code == 200:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'X-Correlation-ID': correlation_id
                },
                'body': json.dumps({
                    'success': True,
                    'data': response.output,
                    'token_usage': response.usage if hasattr(response, 'usage') else {}
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': f'Wanx API error: {response.message}'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
'''

# Global Function Compute service instance
function_compute_service = FunctionComputeService()