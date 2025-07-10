# Real-time Chat Application

A modern, real-time chat application built with FastAPI (backend) and React (frontend).

## Features

- ✅ Real-time messaging with WebSocket
- ✅ User authentication and authorization
- ✅ Multiple chat rooms
- ✅ Private messaging
- ✅ Online status indicators
- ✅ Typing indicators
- ✅ Message history
- ✅ Responsive design
- ✅ Docker deployment

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **WebSocket** - Real-time communication
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **JWT** - Authentication tokens

### Frontend
- **React** - UI framework
- **React Router** - Navigation
- **WebSocket API** - Real-time communication
- **CSS3** - Styling

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Run with Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Rooms
- `GET /api/rooms/` - List all rooms
- `POST /api/rooms/` - Create new room
- `GET /api/rooms/{room_id}` - Get room details
- `GET /api/rooms/{room_id}/messages` - Get room message history

### WebSocket
- `WS /ws/{room_id}` - Connect to room for real-time messaging

## Project Structure

```
chat-application/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── app/
│   │   ├── models/            # Database models
│   │   ├── routes/            # API routes
│   │   └── websocket/         # WebSocket handlers
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   └── App.jsx           # Main app component
│   ├── public/               # Static files
│   └── package.json          # Node.js dependencies
├── docs/                     # Documentation
├── docker-compose.yml        # Docker orchestration
└── README.md                # This file
```

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Deployment

### Production Deployment
1. Set environment variables
2. Build Docker images
3. Deploy with Docker Compose or Kubernetes

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `REDIS_URL` - Redis connection string

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - see LICENSE file for details.
