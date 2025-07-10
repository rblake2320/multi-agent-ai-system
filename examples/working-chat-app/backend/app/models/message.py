"""
Message model for chat messages
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    message_type = Column(String(20), default="text")  # text, image, file
    timestamp = Column(DateTime, default=datetime.utcnow)
    edited_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    sender = relationship("User", back_populates="messages")
    room = relationship("Room", back_populates="messages")
