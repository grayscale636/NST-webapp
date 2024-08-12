import React, { useState } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import UserImages from './components/UserImages';
import ImageUploader from './components/ImageUploader';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
  };

  const handleRegister = () => {
    setShowRegister(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="App">
        <h1>Neural Style Transfer</h1>
        {showRegister ? (
          <Register onRegister={handleRegister} />
        ) : (
          <>
            <Login onLogin={handleLogin} />
            <p>Don't have an account? <button onClick={() => setShowRegister(true)}>Register</button></p>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="App">
      <h1>Neural Style Transfer</h1>
      <button onClick={handleLogout}>Logout</button>
      <ImageUploader />
      <UserImages />
    </div>
  );
}

export default App;