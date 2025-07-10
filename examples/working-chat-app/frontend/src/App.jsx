import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Chat from './pages/Chat';
import RoomList from './pages/RoomList';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      // Verify token and get user info
      fetchUserInfo();
    }
  }, [token]);

  const fetchUserInfo = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('token');
        setToken(null);
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
    }
  };

  const handleLogin = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('token', authToken);
  };

  const handleLogout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/login" 
            element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/rooms" />} 
          />
          <Route 
            path="/rooms" 
            element={user ? <RoomList user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/chat/:roomId" 
            element={user ? <Chat user={user} token={token} /> : <Navigate to="/login" />} 
          />
          <Route path="/" element={<Navigate to={user ? "/rooms" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;