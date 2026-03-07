import { useState } from "react";

interface LoginPageProps {
  onLogin: (username: string, password: string) => Promise<void>;
  onRegister: (data: {
    username: string;
    display_name: string;
    password: string;
    phone_number?: string;
  }) => Promise<void>;
}

export default function LoginPage({ onLogin, onRegister }: LoginPageProps) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isRegister) {
        await onRegister({
          username,
          display_name: displayName,
          password,
          phone_number: phone || undefined,
        });
      } else {
        await onLogin(username, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--sox-navy)",
      }}
    >
      <div className="card" style={{ width: "100%", maxWidth: "400px" }}>
        <h1
          style={{
            textAlign: "center",
            color: "var(--sox-red)",
            marginBottom: "0.5rem",
            fontSize: "1.5rem",
          }}
        >
          Red Sox Ticket Draft
        </h1>
        <p
          style={{
            textAlign: "center",
            color: "var(--text-secondary)",
            marginBottom: "1.5rem",
            fontSize: "0.875rem",
          }}
        >
          {isRegister ? "Create your account" : "Sign in to your account"}
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "1rem" }}>
            <label>Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          {isRegister && (
            <>
              <div style={{ marginBottom: "1rem" }}>
                <label>Display Name</label>
                <input
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="How your friends know you"
                  required
                />
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <label>Phone Number (for SMS notifications)</label>
                <input
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1234567890"
                />
              </div>
            </>
          )}

          <div style={{ marginBottom: "1rem" }}>
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p style={{ color: "var(--sox-red)", fontSize: "0.875rem", marginBottom: "1rem" }}>
              {error}
            </p>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: "100%", justifyContent: "center" }}
          >
            {loading ? "..." : isRegister ? "Create Account" : "Sign In"}
          </button>
        </form>

        <p
          style={{
            textAlign: "center",
            marginTop: "1rem",
            fontSize: "0.875rem",
            color: "var(--text-secondary)",
          }}
        >
          {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError("");
            }}
            style={{
              background: "none",
              border: "none",
              color: "var(--sox-navy)",
              fontWeight: 600,
              cursor: "pointer",
              padding: 0,
              font: "inherit",
            }}
          >
            {isRegister ? "Sign In" : "Register"}
          </button>
        </p>
      </div>
    </div>
  );
}
