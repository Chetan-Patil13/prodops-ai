import { useState, useEffect, useRef } from "react";
import { apiFetch } from "../api/client";
import { Send, LogOut, Loader2, Bot, User } from "lucide-react";

function ChatMessage({ message, isBot }) {
  return (
    <div
      className={`flex gap-4 ${isBot ? "bg-slate-800/50" : ""} p-6 rounded-lg`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isBot ? "bg-blue-600" : "bg-slate-700"
        }`}
      >
        {isBot ? (
          <Bot className="w-5 h-5 text-white" />
        ) : (
          <User className="w-5 h-5 text-white" />
        )}
      </div>
      <div className="flex-1 pt-1">
        <p className="text-slate-200 whitespace-pre-wrap leading-relaxed">
          {message}
        </p>
      </div>
    </div>
  );
}

export default function Chat({ user, onLogout, onViewTickets }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { text: userMessage, isBot: false }]);
    setLoading(true);

    try {
      const res = await apiFetch(
        `/chat/?message=${encodeURIComponent(userMessage)}`,
        {
          method: "POST",
        }
      );

      setMessages((prev) => [...prev, { text: res.reply, isBot: true }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          text: "Sorry, I encountered an error. Please try again.",
          isBot: true,
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
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
            onClick={onLogout}
            className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-600/20 rounded-full mb-4">
                <Bot className="w-10 h-10 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Welcome to ProdOps AI
              </h2>
              <p className="text-slate-400 mb-8">
                How can I assist you with production operations today?
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {[
                  "Show me today's production summary",
                  "What are the open tickets?",
                  "Check downtime for Line A",
                  "Create a maintenance ticket",
                ].map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(suggestion)}
                    className="text-left px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 text-sm transition"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg.text} isBot={msg.isBot} />
            ))
          )}

          {loading && (
            <div className="flex gap-4 bg-slate-800/50 p-6 rounded-lg">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 pt-1">
                <div className="flex gap-1">
                  <div
                    className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"
                    style={{ animationDelay: "0ms" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"
                    style={{ animationDelay: "150ms" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"
                    style={{ animationDelay: "300ms" }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-slate-800/80 backdrop-blur-sm border-t border-slate-700 px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3 items-end">
            <div className="flex-1 bg-slate-900 rounded-xl border border-slate-700 focus-within:border-blue-500 transition">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about production, tickets, downtime..."
                rows="1"
                className="w-full px-4 py-3 bg-transparent text-white placeholder-slate-500 resize-none focus:outline-none"
                style={{ minHeight: "48px", maxHeight: "200px" }}
                disabled={loading}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="flex-shrink-0 w-12 h-12 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-xl flex items-center justify-center transition"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 text-white animate-spin" />
              ) : (
                <Send className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
