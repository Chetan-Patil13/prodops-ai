import { useState } from "react";
import Login from "./pages/Login";
import Chat from "./pages/chat";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("token"));

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  return <Chat />;
}
