export interface User {
  id: number;
  username: string;
  display_name: string;
  phone_number: string | null;
  notification_preference: "sms" | "none";
  is_commissioner: boolean;
  created_at: string;
}

export interface Draft {
  id: number;
  name: string;
  season_year: number;
  status: "setup" | "active" | "paused" | "completed";
  current_round: number;
  current_pick_index: number;
  snake_draft: boolean;
  seats_per_game: number;
  created_by_id: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface DraftDetail extends Draft {
  participants: Participant[];
  games: Game[];
  picks: Pick[];
}

export interface Participant {
  id: number;
  draft_id: number;
  user_id: number;
  draft_order: number;
  user: User;
}

export interface Game {
  id: number;
  draft_id: number;
  opponent: string;
  game_date: string;
  game_time: string | null;
  day_of_week: string | null;
  is_weekend: boolean;
  is_holiday: boolean;
  notes: string | null;
  estimated_demand: number | null;
  seats_available: number;
}

export interface Pick {
  id: number;
  draft_id: number;
  game_id: number;
  user_id: number;
  round_number: number;
  pick_number: number;
  seat_number: number;
  picked_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  suggested_picks?: number[];
}
