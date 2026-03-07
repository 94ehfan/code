import { useState } from "react";
import { ChatMessage } from "../types";
import * as api from "../services/api";

interface AIChatProps {
  draftId: number;
  onPickSuggested?: (gameId: number) => void;
}

export default function AIChat({ draftId, onPickSuggested }: AIChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hey! I'm your draft assistant. Ask me about matchups, strategy, " +
        "or which games to target. Try 'What are the best weekend games left?'",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.chatWithAI(draftId, userMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.response,
          suggested_picks: res.suggested_picks ?? undefined,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Sorry, I hit an error: ${err instanceof Error ? err.message : "Unknown error"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div
        style={{
          background: "var(--sox-navy)",
          color: "white",
          padding: "0.75rem 1rem",
          fontWeight: 600,
          fontSize: "0.875rem",
        }}
      >
        Draft Assistant
      </div>
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <div>{msg.content}</div>
            {msg.suggested_picks && msg.suggested_picks.length > 0 && onPickSuggested && (
              <div style={{ marginTop: "0.5rem" }}>
                {msg.suggested_picks.map((gid) => (
                  <button
                    key={gid}
                    className="btn btn-primary"
                    style={{ marginRight: "0.25rem", padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}
                    onClick={() => onPickSuggested(gid)}
                  >
                    Pick Game {gid}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant" style={{ opacity: 0.6 }}>
            Thinking...
          </div>
        )}
      </div>
      <div className="chat-input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask about games, strategy, matchups..."
          disabled={loading}
        />
        <button className="btn btn-primary" onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
