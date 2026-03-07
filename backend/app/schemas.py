from datetime import datetime

from pydantic import BaseModel

from app.models import DraftStatus, NotificationPreference


# --- Users ---
class UserCreate(BaseModel):
    username: str
    display_name: str
    password: str
    phone_number: str | None = None
    notification_preference: NotificationPreference = NotificationPreference.SMS


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    phone_number: str | None
    notification_preference: NotificationPreference
    is_commissioner: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Drafts ---
class DraftCreate(BaseModel):
    name: str
    season_year: int
    snake_draft: bool = True
    seats_per_game: int = 4


class DraftResponse(BaseModel):
    id: int
    name: str
    season_year: int
    status: DraftStatus
    current_round: int
    current_pick_index: int
    snake_draft: bool
    seats_per_game: int
    created_by_id: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class DraftDetail(DraftResponse):
    participants: list["ParticipantResponse"]
    games: list["GameResponse"]
    picks: list["PickResponse"]


# --- Participants ---
class ParticipantAdd(BaseModel):
    user_id: int
    draft_order: int


class ParticipantResponse(BaseModel):
    id: int
    draft_id: int
    user_id: int
    draft_order: int
    user: UserResponse

    model_config = {"from_attributes": True}


# --- Games ---
class GameCreate(BaseModel):
    opponent: str
    game_date: datetime
    game_time: str | None = None
    day_of_week: str | None = None
    is_weekend: bool = False
    is_holiday: bool = False
    notes: str | None = None


class GameResponse(BaseModel):
    id: int
    draft_id: int
    opponent: str
    game_date: datetime
    game_time: str | None
    day_of_week: str | None
    is_weekend: bool
    is_holiday: bool
    notes: str | None
    estimated_demand: float | None
    seats_available: int = 4

    model_config = {"from_attributes": True}


# --- Picks ---
class PickCreate(BaseModel):
    game_id: int
    seat_number: int | None = None  # auto-assign if not specified


class PickResponse(BaseModel):
    id: int
    draft_id: int
    game_id: int
    user_id: int
    round_number: int
    pick_number: int
    seat_number: int
    picked_at: datetime

    model_config = {"from_attributes": True}


class PickDetail(PickResponse):
    user: UserResponse
    game: GameResponse


# --- AI ---
class AIChatMessage(BaseModel):
    message: str
    draft_id: int


class AIChatResponse(BaseModel):
    response: str
    suggested_picks: list[int] | None = None  # game IDs


class WeeklySummaryResponse(BaseModel):
    summary: str
    generated_at: datetime


# --- Agent API ---
class AgentPickRequest(BaseModel):
    """Schema for external AI agents to make picks."""

    game_id: int
    seat_number: int | None = None
    agent_name: str | None = None
    reasoning: str | None = None


class DraftStateResponse(BaseModel):
    """Full draft state for AI agents to consume."""

    draft: DraftResponse
    participants: list[ParticipantResponse]
    available_games: list[GameResponse]
    picks_made: list[PickDetail]
    current_picker: UserResponse | None
    your_picks: list[PickDetail]
