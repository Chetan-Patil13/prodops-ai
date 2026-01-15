import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

export default function Tickets() {
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    apiFetch("/tickets?limit=10").then(setTickets);
  }, []);

  return (
    <div>
      <h2>Tickets</h2>
      <ul>
        {tickets.map((t) => (
          <li key={t.ticket_no}>
            {t.ticket_no} - {t.status} - {t.severity}
          </li>
        ))}
      </ul>
    </div>
  );
}
