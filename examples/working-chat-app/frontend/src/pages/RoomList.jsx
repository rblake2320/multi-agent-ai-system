import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const RoomList = ({ user, onLogout }) => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateRoom, setShowCreateRoom] = useState(false);
  const [newRoom, setNewRoom] = useState({
    name: '',
    description: '',
    is_private: false
  });

  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/rooms/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRooms(data);
      } else {
        setError('Failed to fetch rooms');
      }
    } catch (error) {
      setError('Network error');
      console.error('Error fetching rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const createRoom = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/rooms/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newRoom)
      });

      if (response.ok) {
        const room = await response.json();
        setRooms([...rooms, room]);
        setNewRoom({ name: '', description: '', is_private: false });
        setShowCreateRoom(false);
      } else {
        setError('Failed to create room');
      }
    } catch (error) {
      setError('Network error');
      console.error('Error creating room:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading rooms...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Chat Rooms</h1>
              <p className="text-gray-600">Welcome back, {user.username}!</p>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowCreateRoom(true)}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Create Room
              </button>
              <button
                onClick={onLogout}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Create Room Modal */}
        {showCreateRoom && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Create New Room</h3>
              <form onSubmit={createRoom}>
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Room Name
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    value={newRoom.name}
                    onChange={(e) => setNewRoom({ ...newRoom, name: e.target.value })}
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Description
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    rows="3"
                    value={newRoom.description}
                    onChange={(e) => setNewRoom({ ...newRoom, description: e.target.value })}
                  />
                </div>
                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="mr-2"
                      checked={newRoom.is_private}
                      onChange={(e) => setNewRoom({ ...newRoom, is_private: e.target.checked })}
                    />
                    Private Room
                  </label>
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateRoom(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Create
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Rooms Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {rooms.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-500 text-xl">No rooms available</p>
              <p className="text-gray-400">Create the first room to get started!</p>
            </div>
          ) : (
            rooms.map((room) => (
              <Link
                key={room.id}
                to={`/chat/${room.id}`}
                className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {room.name}
                    </h3>
                    {room.is_private && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Private
                      </span>
                    )}
                  </div>
                  {room.description && (
                    <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                      {room.description}
                    </p>
                  )}
                  <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                    <span>{room.member_count} member{room.member_count !== 1 ? 's' : ''}</span>
                    <span>Created {formatDate(room.created_at)}</span>
                  </div>
                  {room.last_message && (
                    <div className="mt-2 text-sm text-gray-600 italic truncate">
                      Last: {room.last_message}
                    </div>
                  )}
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default RoomList;

