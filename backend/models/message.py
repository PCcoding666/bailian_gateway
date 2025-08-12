from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from config.database import Base
import json

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum("user", "assistant", "system"), nullable=False)
    content_type = Column(Enum("text", "image_url", "video_url"), default="text")
    content = Column(Text, nullable=False)  # JSON formatted content
    status = Column(Integer, default=1)  # 1-active, 0-deleted
    created_at = Column(DateTime, default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")
    api_calls = relationship("APICall", back_populates="message")

    def to_dict(self):
        """Convert message object to dictionary"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "role": self.role,
            "content_type": self.content_type,
            "content": json.loads(self.content) if self.content else [],
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def set_content(self, content_data):
        """Set content as JSON string"""
        self.content = json.dumps(content_data)

    def get_content(self):
        """Get content as Python object"""
        return json.loads(self.content) if self.content else []