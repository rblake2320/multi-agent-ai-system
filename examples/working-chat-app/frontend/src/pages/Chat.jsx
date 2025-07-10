import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';

const Chat = ({ user, token }) => {
  const { roomId } = useParams();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadRoomInfo();
    loadMessageHistory();
    
    // Poll for new messages every 2 seconds (simplified real-time)
    const interval = setInterval(loadMessageHistory, 2000);
    
    return () => clearInterval(interval);
  }, [roomId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadRoomInfo = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/rooms/${roomId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const roomData = await response.json();
        setRoom(roomData);
      } else {
        setError('Failed to load room information');
      }
    } catch (error) {
      setError('Network error');
      console.error('Error loading room:', error);
    }
  };

  const loadMessageHistory = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/rooms/${roomId}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const messageData = await response.json();
        setMessages(messageData);
      } else {
        setError('Failed to load messages');
      }
    } catch (error) {
      setError('Network error');
      console.error('Error loading messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/api/rooms/${roomId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: newMessage,
          message_type: 'text'
        })
      });

      if (response.ok) {
        setNewMessage('');
        // Reload messages to show the new one
        loadMessageHistory();
      } else {
        setError('Failed to send message');
      }
    } catch (error) {
      setError('Network error');
      console.error('Error sending message:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading chat...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Link
                to="/rooms"
                className="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                ← Back to Rooms
              </Link>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  {room?.name || `Room ${roomId}`}
                </h1>
                {room?.description && (
                  <p className="text-sm text-gray-600">{room.description}</p>
                )}
              </div>
            </div>
            <div className="text-sm text-gray-500">
              {room?.member_count} member{room?.member_count !== 1 ? 's' : ''}
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3">
          {error}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          messages.map((message, index) => {
            const showDate = index === 0 || 
              formatDate(message.timestamp) !== formatDate(messages[index - 1].timestamp);
            
            return (
              <div key={message.id}>
                {showDate && (
                  <div className="text-center text-xs text-gray-500 my-4">
                    {formatDate(message.timestamp)}
                  </div>
                )}
                <div className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.sender_id === user.id
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-900 shadow'
                  }`}>
                    {message.sender_id !== user.id && (
                      <div className="text-xs font-medium text-gray-600 mb-1">
                        {message.sender_username}
                      </div>
                    )}
                    <div className="text-sm">{message.content}</div>
                    <div className={`text-xs mt-1 ${
                      message.sender_id === user.id ? 'text-indigo-200' : 'text-gray-500'
                    }`}>
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="bg-white border-t p-4">
        <form onSubmit={sendMessage} className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={!newMessage.trim()}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;

