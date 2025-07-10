"""
Room management routes for the chat application
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.models.database import get_db
from app.models.room import Room
from app.models.message import Message
from app.models.user import User
from app.routes.auth import get_current_user

rooms_router = APIRouter()

# Pydantic models
class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None

class MessageCreate(BaseModel):
    content: str
    message_type: str = "text"

class MessageResponse(BaseModel):
    id: int
    content: str
    message_type: str
    timestamp: datetime
    sender_id: int
    room_id: int
    is_deleted: bool
    sender_username: str

    class Config:
        from_attributes = True

class RoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_private: bool
    created_at: datetime
    created_by: int
    member_count: int
    last_message: Optional[str] = None

    class Config:
        from_attributes = True

# Routes
@rooms_router.post("/", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat room"""
    db_room = Room(
        name=room_data.name,
        description=room_data.description,
        is_private=room_data.is_private,
        created_by=current_user.id
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    
    # Add creator as member
    # Note: In a full implementation, you'd have a room_members table
    
    # Calculate member count (simplified)
    member_count = 1  # Just the creator for now
    
    return RoomResponse(
        id=db_room.id,
        name=db_room.name,
        description=db_room.description,
        is_private=db_room.is_private,
        created_at=db_room.created_at,
        created_by=db_room.created_by,
        member_count=member_count
    )

@rooms_router.get("/", response_model=List[RoomResponse])
async def list_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """List all available rooms"""
    rooms = db.query(Room).filter(Room.is_private == False).offset(skip).limit(limit).all()
    
    room_responses = []
    for room in rooms:
        # Get last message
        last_message_obj = db.query(Message).filter(
            Message.room_id == room.id,
            Message.is_deleted == False
        ).order_by(Message.timestamp.desc()).first()
        
        last_message = last_message_obj.content if last_message_obj else None
        
        # Count messages as proxy for activity (in real app, you'd count members)
        member_count = db.query(Message).filter(Message.room_id == room.id).count()
        
        room_responses.append(RoomResponse(
            id=room.id,
            name=room.name,
            description=room.description,
            is_private=room.is_private,
            created_at=room.created_at,
            created_by=room.created_by,
            member_count=max(1, member_count),  # At least 1 (creator)
            last_message=last_message
        ))
    
    return room_responses

@rooms_router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific room"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if user has access to private room
    if room.is_private and room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private room")
    
    # Get last message
    last_message_obj = db.query(Message).filter(
        Message.room_id == room.id,
        Message.is_deleted == False
    ).order_by(Message.timestamp.desc()).first()
    
    last_message = last_message_obj.content if last_message_obj else None
    
    # Count members (simplified)
    member_count = max(1, db.query(Message).filter(Message.room_id == room.id).count())
    
    return RoomResponse(
        id=room.id,
        name=room.name,
        description=room.description,
        is_private=room.is_private,
        created_at=room.created_at,
        created_by=room.created_by,
        member_count=member_count,
        last_message=last_message
    )

@rooms_router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a room (only by creator)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only room creator can update room")
    
    # Update fields
    if room_data.name is not None:
        room.name = room_data.name
    if room_data.description is not None:
        room.description = room_data.description
    if room_data.is_private is not None:
        room.is_private = room_data.is_private
    
    db.commit()
    db.refresh(room)
    
    # Get updated info
    member_count = max(1, db.query(Message).filter(Message.room_id == room.id).count())
    
    return RoomResponse(
        id=room.id,
        name=room.name,
        description=room.description,
        is_private=room.is_private,
        created_at=room.created_at,
        created_by=room.created_by,
        member_count=member_count
    )

@rooms_router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a room (only by creator)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only room creator can delete room")
    
    # Delete all messages in the room
    db.query(Message).filter(Message.room_id == room_id).delete()
    
    # Delete the room
    db.delete(room)
    db.commit()
    
    return {"message": "Room deleted successfully"}

@rooms_router.get("/{room_id}/messages", response_model=List[MessageResponse])
async def get_room_messages(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """Get messages from a room"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check access to private room
    if room.is_private and room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private room")
    
    messages = db.query(Message).join(User).filter(
        Message.room_id == room_id,
        Message.is_deleted == False
    ).order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
    
    message_responses = []
    for message in messages:
        sender = db.query(User).filter(User.id == message.sender_id).first()
        message_responses.append(MessageResponse(
            id=message.id,
            content=message.content,
            message_type=message.message_type,
            timestamp=message.timestamp,
            sender_id=message.sender_id,
            room_id=message.room_id,
            is_deleted=message.is_deleted,
            sender_username=sender.username if sender else "Unknown"
        ))
    
    return list(reversed(message_responses))  # Return in chronological order

@rooms_router.post("/{room_id}/messages", response_model=MessageResponse)
async def send_message(
    room_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to a room"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check access to private room
    if room.is_private and room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to private room")
    
    # Create message
    db_message = Message(
        content=message_data.content,
        message_type=message_data.message_type,
        sender_id=current_user.id,
        room_id=room_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return MessageResponse(
        id=db_message.id,
        content=db_message.content,
        message_type=db_message.message_type,
        timestamp=db_message.timestamp,
        sender_id=db_message.sender_id,
        room_id=db_message.room_id,
        is_deleted=db_message.is_deleted,
        sender_username=current_user.username
    )

