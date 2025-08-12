from sqlalchemy.orm import Session
from models import Message, Conversation
from typing import Optional, List

class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, conversation_id: int, user_id: int, role: str, 
                      content: list, content_type: str = "text") -> Message:
        """Create a new message"""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content_type=content_type
        )
        message.set_content(content)
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message

    def get_message_by_id(self, message_id: int, user_id: int) -> Optional[Message]:
        """Get message by ID for a specific user"""
        return self.db.query(Message).filter(
            Message.id == message_id,
            Message.user_id == user_id
        ).first()

    def get_conversation_messages(self, conversation_id: int, user_id: int, 
                                 skip: int = 0, limit: int = 20) -> List[Message]:
        """Get all messages for a conversation"""
        # First verify the conversation belongs to the user
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            return []
        
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()

    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete message"""
        message = self.get_message_by_id(message_id, user_id)
        if not message:
            return False
        
        self.db.delete(message)
        self.db.commit()
        return True