import { Game, Pick } from "../types";

interface GameCardProps {
  game: Game;
  picks: Pick[];
  currentUserId: number | null;
  isMyTurn: boolean;
  seatsPerGame: number;
  onPick: (gameId: number) => void;
}

export default function GameCard({
  game,
  picks,
  currentUserId,
  isMyTurn,
  seatsPerGame,
  onPick,
}: GameCardProps) {
  const gamePicks = picks.filter((p) => p.game_id === game.id);
  const seatsLeft = seatsPerGame - gamePicks.length;
  const iHaveSeat = gamePicks.some((p) => p.user_id === currentUserId);
  const isFull = seatsLeft <= 0;

  const date = new Date(game.game_date);
  const dateStr = date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  let className = "pick-card";
  if (iHaveSeat) className += " mine";
  else if (isFull) className += " taken";
  else if (isMyTurn) className += " available";

  return (
    <div
      className={className}
      onClick={() => {
        if (isMyTurn && !isFull) onPick(game.id);
      }}
      title={
        isMyTurn && !isFull
          ? "Click to pick this game"
          : isFull
            ? "All seats taken"
            : ""
      }
    >
      <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>{dateStr}</div>
      <div style={{ color: "var(--text-secondary)" }}>vs {game.opponent}</div>
      <div style={{ marginTop: "0.25rem" }}>
        {isFull ? (
          <span style={{ color: "var(--sox-gray)" }}>Full</span>
        ) : (
          <span style={{ color: "var(--success)" }}>
            {seatsLeft}/{seatsPerGame} seats
          </span>
        )}
      </div>
      {(game.is_weekend || game.is_holiday) && (
        <div style={{ marginTop: "0.25rem" }}>
          {game.is_weekend && (
            <span className="badge badge-active" style={{ marginRight: "0.25rem" }}>
              Weekend
            </span>
          )}
          {game.is_holiday && (
            <span className="badge badge-setup">Holiday</span>
          )}
        </div>
      )}
    </div>
  );
}
