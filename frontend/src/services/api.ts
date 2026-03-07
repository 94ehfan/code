const API_BASE = "/api";

function getToken(): string | null {
  return localStorage.getItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || "Request failed");
  }

  return res.json();
}

// Auth
export const login = (username: string, password: string) =>
  request<{ access_token: string }>("/users/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

export const register = (data: {
  username: string;
  display_name: string;
  password: string;
  phone_number?: string;
}) =>
  request<{ access_token: string }>("/users/register", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const getMe = () => request<import("../types").User>("/users/me");

// Drafts
export const getDrafts = () =>
  request<import("../types").Draft[]>("/drafts/");

export const getDraft = (id: number) =>
  request<import("../types").DraftDetail>(`/drafts/${id}`);

export const createDraft = (data: {
  name: string;
  season_year: number;
  snake_draft?: boolean;
  seats_per_game?: number;
}) =>
  request<import("../types").Draft>("/drafts/", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const startDraft = (id: number) =>
  request<import("../types").Draft>(`/drafts/${id}/start`, { method: "POST" });

export const pauseDraft = (id: number) =>
  request<import("../types").Draft>(`/drafts/${id}/pause`, { method: "POST" });

export const resumeDraft = (id: number) =>
  request<import("../types").Draft>(`/drafts/${id}/resume`, { method: "POST" });

export const addParticipant = (draftId: number, userId: number, draftOrder: number) =>
  request(`/drafts/${draftId}/participants`, {
    method: "POST",
    body: JSON.stringify({ user_id: userId, draft_order: draftOrder }),
  });

export const addGame = (
  draftId: number,
  game: {
    opponent: string;
    game_date: string;
    game_time?: string;
    day_of_week?: string;
    is_weekend?: boolean;
    is_holiday?: boolean;
    notes?: string;
  }
) =>
  request(`/drafts/${draftId}/games`, {
    method: "POST",
    body: JSON.stringify(game),
  });

export const addGamesBulk = (
  draftId: number,
  games: Array<{
    opponent: string;
    game_date: string;
    game_time?: string;
    day_of_week?: string;
    is_weekend?: boolean;
    is_holiday?: boolean;
  }>
) =>
  request(`/drafts/${draftId}/games/bulk`, {
    method: "POST",
    body: JSON.stringify(games),
  });

// Picks
export const makePick = (draftId: number, gameId: number, seatNumber?: number) =>
  request<import("../types").Pick>(`/drafts/${draftId}/picks/`, {
    method: "POST",
    body: JSON.stringify({ game_id: gameId, seat_number: seatNumber }),
  });

export const getMyPicks = (draftId: number) =>
  request<import("../types").Pick[]>(`/drafts/${draftId}/picks/my`);

// AI
export const chatWithAI = (draftId: number, message: string) =>
  request<{ response: string; suggested_picks?: number[] }>("/ai/chat", {
    method: "POST",
    body: JSON.stringify({ draft_id: draftId, message }),
  });

export const getWeeklySummary = (draftId: number) =>
  request<{ summary: string; generated_at: string }>(`/ai/summary/${draftId}`);

// Users
export const listUsers = () =>
  request<import("../types").User[]>("/users/");
