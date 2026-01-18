import { useState, useEffect } from "react";
import { apiFetch } from "../api/client";
import {
  Ticket,
  AlertCircle,
  CheckCircle2,
  Clock,
  Filter,
  RefreshCw,
  X,
} from "lucide-react";

export default function TicketManagement({ user, onBack }) {
  // ... rest of your code
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("ALL");
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchData();
  }, [filter]);

  async function fetchData() {
    setLoading(true);
    try {
      const [ticketsData, statsData] = await Promise.all([
        apiFetch(`/tickets${filter !== "ALL" ? `?status=${filter}` : ""}`),
        apiFetch("/tickets/stats"),
      ]);
      setTickets(ticketsData);
      setStats(statsData);
    } catch (err) {
      console.error("Failed to fetch tickets:", err);
    } finally {
      setLoading(false);
    }
  }

  async function updateTicketStatus(ticketNo, newStatus) {
    setUpdating(true);
    try {
      await apiFetch(`/tickets/${ticketNo}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });

      // Refresh data
      await fetchData();
      setSelectedTicket(null);
    } catch (err) {
      alert("Failed to update ticket: " + err.message);
    } finally {
      setUpdating(false);
    }
  }

  const getSeverityColor = (severity) => {
    const colors = {
      Critical: "bg-red-500",
      High: "bg-orange-500",
      Medium: "bg-yellow-500",
      Low: "bg-green-500",
    };
    return colors[severity] || "bg-gray-500";
  };

  const getStatusColor = (status) => {
    const colors = {
      OPEN: "bg-blue-500",
      IN_PROGRESS: "bg-yellow-500",
      CLOSED: "bg-green-500",
    };
    return colors[status] || "bg-gray-500";
  };

  const getStatusIcon = (status) => {
    if (status === "CLOSED") return <CheckCircle2 className="w-4 h-4" />;
    if (status === "IN_PROGRESS") return <Clock className="w-4 h-4" />;
    return <AlertCircle className="w-4 h-4" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/80 backdrop-blur-sm border-b border-slate-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">ProdOps AI</h1>
            <p className="text-xs text-slate-400">Production Assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right hidden sm:block">
            <p className="text-sm text-slate-300">{user.email}</p>
            <p className="text-xs text-slate-500">{user.roles?.join(", ")}</p>
          </div>
          <button
            onClick={onViewTickets}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
          >
            <Ticket className="w-4 h-4" />
            <span className="hidden sm:inline">Tickets</span>
          </button>
          <button
            onClick={onLogout}
            className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Open Tickets</p>
                  <p className="text-3xl font-bold text-blue-400">
                    {stats.open_count}
                  </p>
                </div>
                <AlertCircle className="w-12 h-12 text-blue-400 opacity-20" />
              </div>
            </div>

            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">In Progress</p>
                  <p className="text-3xl font-bold text-yellow-400">
                    {stats.in_progress_count}
                  </p>
                </div>
                <Clock className="w-12 h-12 text-yellow-400 opacity-20" />
              </div>
            </div>

            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Closed</p>
                  <p className="text-3xl font-bold text-green-400">
                    {stats.closed_count}
                  </p>
                </div>
                <CheckCircle2 className="w-12 h-12 text-green-400 opacity-20" />
              </div>
            </div>

            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Total</p>
                  <p className="text-3xl font-bold text-white">
                    {stats.total_count}
                  </p>
                </div>
                <Ticket className="w-12 h-12 text-white opacity-20" />
              </div>
            </div>
          </div>
        )}

        {/* Filter Buttons */}
        <div className="flex gap-2 mb-6">
          {["ALL", "OPEN", "IN_PROGRESS", "CLOSED"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg transition ${
                filter === f
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {f.replace("_", " ")}
            </button>
          ))}
        </div>

        {/* Tickets List */}
        <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-slate-400">
              Loading tickets...
            </div>
          ) : tickets.length === 0 ? (
            <div className="p-12 text-center text-slate-400">
              No tickets found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-900">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Ticket No
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Issue
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Line
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Severity
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Created
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {tickets.map((ticket) => (
                    <tr
                      key={ticket.id}
                      className="hover:bg-slate-700/50 transition"
                    >
                      <td className="px-6 py-4">
                        <span className="font-mono text-blue-400">
                          {ticket.ticket_no}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-200 max-w-xs truncate">
                        {ticket.issue_summary}
                      </td>
                      <td className="px-6 py-4 text-slate-300">
                        {ticket.line_code}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${getSeverityColor(
                            ticket.severity
                          )}`}
                        >
                          {ticket.severity}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold text-white ${getStatusColor(
                            ticket.status
                          )}`}
                        >
                          {getStatusIcon(ticket.status)}
                          {ticket.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-300 text-sm">
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => setSelectedTicket(ticket)}
                          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition"
                        >
                          Update
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Update Status Modal */}
      {selectedTicket && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-2xl p-6 max-w-md w-full border border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">
                Update Ticket Status
              </h3>
              <button
                onClick={() => setSelectedTicket(null)}
                className="text-slate-400 hover:text-white transition"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="mb-6">
              <p className="text-slate-400 text-sm mb-1">Ticket Number</p>
              <p className="text-white font-mono">{selectedTicket.ticket_no}</p>
            </div>

            <div className="mb-6">
              <p className="text-slate-400 text-sm mb-1">Issue</p>
              <p className="text-white">{selectedTicket.issue_summary}</p>
            </div>

            <div className="mb-6">
              <p className="text-slate-400 text-sm mb-2">Current Status</p>
              <span
                className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold text-white ${getStatusColor(
                  selectedTicket.status
                )}`}
              >
                {getStatusIcon(selectedTicket.status)}
                {selectedTicket.status.replace("_", " ")}
              </span>
            </div>

            <div className="space-y-2">
              <p className="text-slate-400 text-sm mb-2">Update to:</p>
              {["OPEN", "IN_PROGRESS", "CLOSED"].map((status) => (
                <button
                  key={status}
                  onClick={() =>
                    updateTicketStatus(selectedTicket.ticket_no, status)
                  }
                  disabled={updating || selectedTicket.status === status}
                  className={`w-full px-4 py-3 rounded-lg transition flex items-center gap-2 ${
                    selectedTicket.status === status
                      ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                      : "bg-slate-700 hover:bg-slate-600 text-white"
                  }`}
                >
                  {getStatusIcon(status)}
                  {status.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
