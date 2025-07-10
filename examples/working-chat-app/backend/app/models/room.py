"""
Room model for chat rooms
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    is_private = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="room")
    memberships = relationship("RoomMembership", back_populates="room")

class RoomMembership(Base):
    __tablename__ = "room_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String(20), default="member")  # admin, moderator, member
    
    # Relationships
    user = relationship("User", back_populates="room_memberships")
    room = relationship("Room", back_populates="memberships")
