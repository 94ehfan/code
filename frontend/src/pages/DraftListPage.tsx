import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Draft } from "../types";
import * as api from "../services/api";

export default function DraftListPage() {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [year, setYear] = useState(new Date().getFullYear());

  useEffect(() => {
    api
      .getDrafts()
      .then(setDrafts)
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const draft = await api.createDraft({ name, season_year: year });
    setDrafts((prev) => [...prev, draft]);
    setShowCreate(false);
    setName("");
  };

  const statusBadge = (status: Draft["status"]) => (
    <span className={`badge badge-${status}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );

  if (loading) return <div className="container" style={{ padding: "2rem" }}>Loading...</div>;

  return (
    <div className="container" style={{ padding: "2rem 1rem" }}>
      <div className="page-header">
        <h1 className="page-title">Your Drafts</h1>
        <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)}>
          + New Draft
        </button>
      </div>

      {showCreate && (
        <div className="card" style={{ marginBottom: "1.5rem" }}>
          <form onSubmit={handleCreate} style={{ display: "flex", gap: "1rem", alignItems: "flex-end", flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: "200px" }}>
              <label>Draft Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. 2026 Red Sox Weekend Games"
                required
              />
            </div>
            <div style={{ width: "120px" }}>
              <label>Season Year</label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(parseInt(e.target.value))}
                required
              />
            </div>
            <button type="submit" className="btn btn-secondary">
              Create
            </button>
          </form>
        </div>
      )}

      {drafts.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
          <p style={{ color: "var(--text-secondary)", marginBottom: "1rem" }}>
            No drafts yet. Create one to get started!
          </p>
        </div>
      ) : (
        <div className="grid grid-2">
          {drafts.map((draft) => (
            <Link
              key={draft.id}
              to={`/draft/${draft.id}`}
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <div className="card" style={{ cursor: "pointer", transition: "box-shadow 0.15s" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                  <h3 style={{ fontSize: "1.125rem" }}>{draft.name}</h3>
                  {statusBadge(draft.status)}
                </div>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
                  {draft.season_year} Season &middot; Round {draft.current_round}
                  {draft.snake_draft ? " &middot; Snake Draft" : ""}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
