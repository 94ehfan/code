import { Link, useLocation } from "react-router-dom";
import { User } from "../types";

interface NavbarProps {
  user: User | null;
  onLogout: () => void;
}

export default function Navbar({ user, onLogout }: NavbarProps) {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/" className="navbar-brand">
          Red Sox Ticket Draft
        </Link>
        {user && (
          <div className="navbar-links">
            <Link
              to="/"
              className={location.pathname === "/" ? "active" : ""}
            >
              Drafts
            </Link>
            <span style={{ color: "rgba(255,255,255,0.6)", fontSize: "0.8rem" }}>
              {user.display_name}
            </span>
            <button
              onClick={onLogout}
              className="btn"
              style={{
                background: "rgba(255,255,255,0.15)",
                color: "white",
                padding: "0.375rem 0.75rem",
                fontSize: "0.8rem",
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
