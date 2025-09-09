"""
Tests for main FastAPI application
"""

import pytest

try:
    from fastapi.testclient import TestClient
    from main import app
except ModuleNotFoundError:  # pragma: no cover - dependency missing
    pytest.skip("fastapi not installed", allow_module_level=True)

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Real-time Chat Application API" in response.json()["message"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_websocket_connection():
    with client.websocket_connect("/ws/test-room") as websocket:
        # Test basic WebSocket connection
        websocket.send_text('{"type": "test", "message": "hello"}')
        data = websocket.receive_text()
        assert data is not None


class TestAuthentication:
    def test_register_user(self):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "uniquetestuser",
                "email": "uniquetest@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 201
        assert "id" in response.json()

    def test_login_user(self):
        # First register a user
        client.post(
            "/api/auth/register",
            json={
                "username": "logintest",
                "email": "logintest@example.com",
                "password": "testpass123",
            },
        )

        # Then login
        response = client.post(
            "/api/auth/login", json={"username": "logintest", "password": "testpass123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestRooms:
    def test_create_room(self):
        # Login first to get token
        login_response = client.post(
            "/api/auth/login", json={"username": "logintest", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]

        response = client.post(
            "/api/rooms/",
            json={"name": "Test Room", "description": "A test room"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Room"

    def test_list_rooms(self):
        # Login first to get token
        login_response = client.post(
            "/api/auth/login", json={"username": "logintest", "password": "testpass123"}
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/rooms/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
