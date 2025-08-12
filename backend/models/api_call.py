from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from config.database import Base

class APICall(Base):
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    model_name = Column(String(100), nullable=False)
    api_endpoint = Column(String(255), nullable=False)
    request_content = Column(Text)  # JSON formatted request
    response_content = Column(Text)  # JSON formatted response
    status_code = Column(SmallInteger)
    request_tokens = Column(Integer, default=0)
    response_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    call_duration = Column(Integer)  # milliseconds
    client_ip = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="api_calls")
    conversation = relationship("Conversation", back_populates="api_calls")
    message = relationship("Message", back_populates="api_calls")

    def to_dict(self):
        """Convert API call object to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "message_id": self.message_id,
            "model_name": self.model_name,
            "api_endpoint": self.api_endpoint,
            "status_code": self.status_code,
            "request_tokens": self.request_tokens,
            "response_tokens": self.response_tokens,
            "total_tokens": self.total_tokens,
            "call_duration": self.call_duration,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }