"""
WebSocket connection manager for real-time communication
"""
from fastapi import WebSocket
from typing import Dict, List
import json
import jwt
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # Store active connections by room
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Store user info for each connection
        self.connection_users: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, token: str = None):
        await websocket.accept()
        
        # Verify token and get user info
        user_info = self._verify_token(token) if token else {"user_id": "anonymous", "username": "Anonymous"}
        
        # Add to room connections
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        self.active_connections[room_id].append(websocket)
        self.connection_users[websocket] = {**user_info, "room_id": room_id}
        
        # Notify room about new user
        await self.broadcast_to_room(room_id, json.dumps({
            "type": "user_joined",
            "user": user_info,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            
        user_info = self.connection_users.pop(websocket, {})
        
        # Notify room about user leaving
        if room_id in self.active_connections:
            asyncio.create_task(self.broadcast_to_room(room_id, json.dumps({
                "type": "user_left", 
                "user": user_info,
                "timestamp": datetime.utcnow().isoformat()
            })))
    
    async def broadcast_to_room(self, room_id: str, message: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.active_connections[room_id].remove(connection)
    
    def _verify_token(self, token: str) -> dict:
        try:
            # In a real app, verify JWT token
            payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
            return {"user_id": payload["user_id"], "username": payload["username"]}
        except:
            return {"user_id": "anonymous", "username": "Anonymous"}
    
    def get_room_users(self, room_id: str) -> List[dict]:
        if room_id not in self.active_connections:
            return []
        
        users = []
        for connection in self.active_connections[room_id]:
            if connection in self.connection_users:
                users.append(self.connection_users[connection])
        return users
