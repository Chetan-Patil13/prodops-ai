import { useState } from "react";
import { apiFetch, setToken } from "../api/client";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");

  async function handleLogin() {
    try {
      const res = await apiFetch(`/auth/login?email=${email}`, {
        method: "POST",
      });
      setToken(res.access_token);
      onLogin();
    } catch (err) {
      alert("Login failed");
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2>ProdOps Login</h2>

        <input
          style={styles.input}
          placeholder="supervisor1@prodops.ai"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <button style={styles.button} onClick={handleLogin}>
          Login
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    background: "#1e1e1e",
    padding: "24px",
    borderRadius: "8px",
    width: "300px",
  },
  input: {
    width: "100%",
    padding: "8px",
    marginTop: "12px",
    marginBottom: "12px",
  },
  button: {
    width: "100%",
    padding: "8px",
    cursor: "pointer",
  },
};
