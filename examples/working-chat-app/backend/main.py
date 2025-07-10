"""
Real-time Chat Application Backend
FastAPI with WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime

from app.models.database import engine, Base
from app.routes.auth import auth_router
from app.routes.rooms import rooms_router
from app.websocket.connection_manager import ConnectionManager

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-time Chat Application", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(rooms_router, prefix="/api/rooms", tags=["rooms"])

@app.get("/")
async def root():
    return {"message": "Real-time Chat Application API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, token: str = None):
    await manager.connect(websocket, room_id, token)
    try:
        while True:
            data = await websocket.receive_text()
            json.loads(data)
            
            # Save message to database
            # Broadcast to room members
            await manager.broadcast_to_room(room_id, data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
