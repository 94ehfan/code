import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class DraftStatus(str, enum.Enum):
    SETUP = "setup"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class NotificationPreference(str, enum.Enum):
    SMS = "sms"
    NONE = "none"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    notification_preference = Column(
        Enum(NotificationPreference), default=NotificationPreference.SMS
    )
    is_commissioner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    draft_participants = relationship("DraftParticipant", back_populates="user")
    picks = relationship("Pick", back_populates="user")


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    season_year = Column(Integer, nullable=False)
    status = Column(Enum(DraftStatus), default=DraftStatus.SETUP)
    current_round = Column(Integer, default=1)
    current_pick_index = Column(Integer, default=0)
    snake_draft = Column(Boolean, default=True)
    seats_per_game = Column(Integer, default=4)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    created_by = relationship("User")
    participants = relationship("DraftParticipant", back_populates="draft")
    games = relationship("Game", back_populates="draft")
    picks = relationship("Pick", back_populates="draft")


class DraftParticipant(Base):
    __tablename__ = "draft_participants"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    draft_order = Column(Integer, nullable=False)

    draft = relationship("Draft", back_populates="participants")
    user = relationship("User", back_populates="draft_participants")

    __table_args__ = (
        UniqueConstraint("draft_id", "user_id", name="uq_draft_user"),
        UniqueConstraint("draft_id", "draft_order", name="uq_draft_order"),
    )


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=False)
    opponent = Column(String(100), nullable=False)
    game_date = Column(DateTime, nullable=False)
    game_time = Column(String(20), nullable=True)
    day_of_week = Column(String(10), nullable=True)
    is_weekend = Column(Boolean, default=False)
    is_holiday = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    estimated_demand = Column(Float, nullable=True)  # AI-suggested desirability

    draft = relationship("Draft", back_populates="games")
    picks = relationship("Pick", back_populates="game")


class Pick(Base):
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    pick_number = Column(Integer, nullable=False)  # overall pick number
    seat_number = Column(Integer, nullable=False)  # which seat (1-4)
    picked_at = Column(DateTime, default=datetime.utcnow)

    draft = relationship("Draft", back_populates="picks")
    game = relationship("Game", back_populates="picks")
    user = relationship("User", back_populates="picks")

    __table_args__ = (
        UniqueConstraint(
            "draft_id", "game_id", "seat_number", name="uq_game_seat"
        ),
    )
