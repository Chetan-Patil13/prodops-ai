import { useState, useEffect } from "react";
import Login from "./pages/Login";
import Chat from "./pages/chat";
import TicketManagement from "./pages/TicketManagement";
import { getToken, getUser, clearAuth } from "./api/client";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState("chat"); // "chat" or "tickets"

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
    setCurrentView("chat");
  }

  if (!loggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  if (currentView === "tickets") {
    return (
      <TicketManagement user={user} onBack={() => setCurrentView("chat")} />
    );
  }

  return (
    <Chat
      user={user}
      onLogout={handleLogout}
      onViewTickets={() => setCurrentView("tickets")}
    />
  );
}
