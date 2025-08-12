from sqlalchemy.orm import Session
from models import APICall
from typing import Optional
import json

class APICallService:
    def __init__(self, db: Session):
        self.db = db

    def log_api_call(self, user_id: int, api_endpoint: str, model_name: str,
                    request_content: dict = None, response_content: dict = None,
                    status_code: int = None, request_tokens: int = 0,
                    response_tokens: int = 0, total_tokens: int = 0,
                    call_duration: int = 0, client_ip: str = None,
                    user_agent: str = None, conversation_id: int = None,
                    message_id: int = None) -> APICall:
        """Log an API call"""
        api_call = APICall(
            user_id=user_id,
            api_endpoint=api_endpoint,
            model_name=model_name,
            request_content=json.dumps(request_content) if request_content else None,
            response_content=json.dumps(response_content) if response_content else None,
            status_code=status_code,
            request_tokens=request_tokens,
            response_tokens=response_tokens,
            total_tokens=total_tokens,
            call_duration=call_duration,
            client_ip=client_ip,
            user_agent=user_agent,
            conversation_id=conversation_id,
            message_id=message_id
        )
        
        self.db.add(api_call)
        self.db.commit()
        self.db.refresh(api_call)
        
        return api_call

    def get_user_api_calls(self, user_id: int, skip: int = 0, limit: int = 10) -> list:
        """Get API calls for a user"""
        return self.db.query(APICall).filter(
            APICall.user_id == user_id
        ).order_by(APICall.created_at.desc()).offset(skip).limit(limit).all()