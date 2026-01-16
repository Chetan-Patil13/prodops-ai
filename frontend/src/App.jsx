import { useState, useEffect } from "react";
import Login from "./pages/Login";
import Chat from "./pages/chat";
import { getToken, getUser, clearAuth } from "./api/client";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = getToken();
    const savedUser = getUser();
    if (token && savedUser) {
      setUser(savedUser);
      setLoggedIn(true);
    }
  }, []);

  function handleLogin(userData) {
    setUser(userData);
    setLoggedIn(true);
  }

  function handleLogout() {
    clearAuth();
    setUser(null);
    setLoggedIn(false);
  }

  if (!loggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return <Chat user={user} onLogout={handleLogout} />;
}
