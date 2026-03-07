import { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { DraftDetail, User } from "../types";
import * as api from "../services/api";
import { useWebSocket } from "../hooks/useWebSocket";
import GameCard from "../components/GameCard";
import AIChat from "../components/AIChat";

interface DraftPageProps {
  currentUser: User;
}

export default function DraftPage({ currentUser }: DraftPageProps) {
  const { id } = useParams<{ id: string }>();
  const draftId = parseInt(id!);
  const [draft, setDraft] = useState<DraftDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showChat, setShowChat] = useState(false);
  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [pickLoading, setPickLoading] = useState(false);

  const loadDraft = useCallback(async () => {
    try {
      const data = await api.getDraft(draftId);
      setDraft(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load draft");
    } finally {
      setLoading(false);
    }
  }, [draftId]);

  useEffect(() => {
    loadDraft();
  }, [loadDraft]);

  // Real-time updates
  useWebSocket(draftId, () => {
    loadDraft();
  });

  const getCurrentPickerUserId = (): number | null => {
    if (!draft || draft.status !== "active") return null;
    const participants = [...draft.participants].sort(
      (a, b) => a.draft_order - b.draft_order
    );
    const n = participants.length;
    if (n === 0) return null;
    const idx = draft.current_pick_index;
    if (draft.snake_draft) {
      const cycle = 2 * n;
      const pos = idx % cycle;
      const orderIdx = pos < n ? pos : cycle - 1 - pos;
      return participants[orderIdx].user_id;
    }
    return participants[idx % n].user_id;
  };

  const currentPickerUserId = draft ? getCurrentPickerUserId() : null;
  const isMyTurn = currentPickerUserId === currentUser.id;

  const handlePick = async (gameId: number) => {
    if (!draft || pickLoading) return;
    setPickLoading(true);
    try {
      await api.makePick(draftId, gameId);
      await loadDraft();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to make pick");
    } finally {
      setPickLoading(false);
    }
  };

  const handleStart = async () => {
    await api.startDraft(draftId);
    await loadDraft();
  };

  const handlePause = async () => {
    await api.pauseDraft(draftId);
    await loadDraft();
  };

  const handleResume = async () => {
    await api.resumeDraft(draftId);
    await loadDraft();
  };

  const loadSummary = async () => {
    setSummaryLoading(true);
    try {
      const res = await api.getWeeklySummary(draftId);
      setSummary(res.summary);
    } catch (err) {
      setSummary(
        `Failed to generate summary: ${err instanceof Error ? err.message : "Unknown error"}`
      );
    } finally {
      setSummaryLoading(false);
    }
  };

  if (loading)
    return (
      <div className="container" style={{ padding: "2rem" }}>
        Loading draft...
      </div>
    );
  if (error || !draft)
    return (
      <div className="container" style={{ padding: "2rem", color: "var(--sox-red)" }}>
        {error || "Draft not found"}
      </div>
    );

  const currentPicker = draft.participants.find(
    (p) => p.user_id === currentPickerUserId
  );

  return (
    <div className="container" style={{ padding: "2rem 1rem" }}>
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">{draft.name}</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            {draft.season_year} &middot; Round {draft.current_round} &middot;{" "}
            <span className={`badge badge-${draft.status}`}>
              {draft.status.charAt(0).toUpperCase() + draft.status.slice(1)}
            </span>
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {draft.status === "setup" &&
            draft.created_by_id === currentUser.id && (
              <button className="btn btn-primary" onClick={handleStart}>
                Start Draft
              </button>
            )}
          {draft.status === "active" &&
            draft.created_by_id === currentUser.id && (
              <button className="btn btn-outline" onClick={handlePause}>
                Pause
              </button>
            )}
          {draft.status === "paused" &&
            draft.created_by_id === currentUser.id && (
              <button className="btn btn-primary" onClick={handleResume}>
                Resume
              </button>
            )}
          <button
            className="btn btn-outline"
            onClick={() => setShowChat(!showChat)}
          >
            {showChat ? "Hide" : "Show"} AI Assistant
          </button>
          <button
            className="btn btn-outline"
            onClick={loadSummary}
            disabled={summaryLoading}
          >
            {summaryLoading ? "Generating..." : "Weekly Summary"}
          </button>
        </div>
      </div>

      {/* Your Turn Banner */}
      {isMyTurn && draft.status === "active" && (
        <div className="your-turn-banner">
          It's your turn to pick! Select a game below.
        </div>
      )}

      {/* Current Picker Info */}
      {draft.status === "active" && currentPicker && !isMyTurn && (
        <div
          className="card"
          style={{
            marginBottom: "1rem",
            textAlign: "center",
            padding: "1rem",
          }}
        >
          Waiting for <strong>{currentPicker.user.display_name}</strong> to pick
          (Round {draft.current_round})
        </div>
      )}

      {/* Weekly Summary */}
      {summary && (
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <h3 style={{ marginBottom: "0.5rem", color: "var(--sox-navy)" }}>
            Weekly Recap
          </h3>
          <p style={{ whiteSpace: "pre-wrap", fontSize: "0.9rem", lineHeight: 1.7 }}>
            {summary}
          </p>
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: showChat ? "1fr 380px" : "1fr",
          gap: "1.5rem",
        }}
      >
        {/* Main Content */}
        <div>
          {/* Draft Board */}
          <div className="draft-board" style={{ marginBottom: "1.5rem" }}>
            <div className="draft-sidebar">
              <div
                style={{
                  padding: "0.75rem 1rem",
                  fontWeight: 700,
                  borderBottom: "1px solid rgba(255,255,255,0.2)",
                }}
              >
                Draft Order
              </div>
              {[...draft.participants]
                .sort((a, b) => a.draft_order - b.draft_order)
                .map((p) => (
                  <div
                    key={p.id}
                    className={`draft-participant ${p.user_id === currentPickerUserId ? "current" : ""}`}
                  >
                    {p.draft_order}. {p.user.display_name}
                    <span style={{ opacity: 0.7, marginLeft: "0.5rem" }}>
                      (
                      {
                        draft.picks.filter((pk) => pk.user_id === p.user_id)
                          .length
                      }{" "}
                      picks)
                    </span>
                  </div>
                ))}
            </div>

            <div className="draft-picks-grid">
              {[...draft.games]
                .sort(
                  (a, b) =>
                    new Date(a.game_date).getTime() -
                    new Date(b.game_date).getTime()
                )
                .map((game) => (
                  <GameCard
                    key={game.id}
                    game={game}
                    picks={draft.picks}
                    currentUserId={currentUser.id}
                    isMyTurn={isMyTurn && draft.status === "active"}
                    seatsPerGame={draft.seats_per_game}
                    onPick={handlePick}
                  />
                ))}
            </div>
          </div>

          {/* My Picks Summary */}
          <div className="card">
            <h3 style={{ marginBottom: "0.75rem", color: "var(--sox-navy)" }}>
              My Picks
            </h3>
            {draft.picks.filter((p) => p.user_id === currentUser.id).length ===
            0 ? (
              <p style={{ color: "var(--text-secondary)" }}>
                No picks yet.
              </p>
            ) : (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                {draft.picks
                  .filter((p) => p.user_id === currentUser.id)
                  .map((pick) => {
                    const game = draft.games.find(
                      (g) => g.id === pick.game_id
                    );
                    if (!game) return null;
                    const date = new Date(game.game_date);
                    return (
                      <div
                        key={pick.id}
                        className="card"
                        style={{
                          padding: "0.5rem 0.75rem",
                          borderColor: "var(--sox-red)",
                          fontSize: "0.8rem",
                        }}
                      >
                        <div style={{ fontWeight: 600 }}>
                          {date.toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                          })}
                        </div>
                        <div>vs {game.opponent}</div>
                        <div style={{ color: "var(--text-secondary)" }}>
                          Seat {pick.seat_number}
                        </div>
                      </div>
                    );
                  })}
              </div>
            )}
          </div>
        </div>

        {/* AI Chat Sidebar */}
        {showChat && (
          <div>
            <AIChat draftId={draftId} onPickSuggested={handlePick} />
          </div>
        )}
      </div>
    </div>
  );
}
