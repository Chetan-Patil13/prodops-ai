import { useState } from "react";
import { apiFetch } from "../api/client";

export default function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  async function sendMessage() {
    const res = await apiFetch(
      `/chat/?message=${encodeURIComponent(message)}`,
      {
        method: "POST",
      }
    );

    setMessages([...messages, { user: message, bot: res.reply }]);
    setMessage("");
  }

  return (
    <div>
      <h2>ProdOps AI</h2>
      <div>
        {messages.map((m, i) => (
          <div key={i}>
            <b>You:</b> {m.user}
            <br />
            <b>AI:</b> {m.bot}
            <hr />
          </div>
        ))}
      </div>

      <input value={message} onChange={(e) => setMessage(e.target.value)} />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
