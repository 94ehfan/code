import logging

import anthropic
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Draft, Game, Pick, User
from app.schemas import AIChatResponse

logger = logging.getLogger(__name__)


def _get_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


def _build_draft_context(draft: Draft, db: Session, user: User | None = None) -> str:
    """Build a text summary of the draft state for the AI."""
    participants = draft.participants
    games = db.query(Game).filter(Game.draft_id == draft.id).order_by(Game.game_date).all()
    picks = (
        db.query(Pick)
        .filter(Pick.draft_id == draft.id)
        .order_by(Pick.pick_number)
        .all()
    )

    lines = [
        f"Draft: {draft.name} ({draft.season_year} season)",
        f"Status: {draft.status.value}, Round: {draft.current_round}",
        f"Format: {'Snake' if draft.snake_draft else 'Linear'} draft, {draft.seats_per_game} seats per game",
        "",
        "Participants (draft order):",
    ]
    for p in sorted(participants, key=lambda x: x.draft_order):
        pick_count = sum(1 for pk in picks if pk.user_id == p.user_id)
        lines.append(f"  {p.draft_order}. {p.user.display_name} — {pick_count} picks")

    lines.append("")
    lines.append("Available games:")
    for game in games:
        taken = sum(1 for pk in picks if pk.game_id == game.id)
        seats_left = draft.seats_per_game - taken
        if seats_left > 0:
            flags = []
            if game.is_weekend:
                flags.append("WEEKEND")
            if game.is_holiday:
                flags.append("HOLIDAY")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            lines.append(
                f"  Game {game.id}: {game.game_date.strftime('%a %b %d')} vs {game.opponent}"
                f" — {seats_left} seat(s) left{flag_str}"
            )

    if user:
        lines.append("")
        lines.append(f"Your picks ({user.display_name}):")
        user_picks = [pk for pk in picks if pk.user_id == user.id]
        if user_picks:
            for pk in user_picks:
                game = db.query(Game).filter(Game.id == pk.game_id).first()
                lines.append(
                    f"  Round {pk.round_number}: {game.game_date.strftime('%a %b %d')} vs {game.opponent}"
                )
        else:
            lines.append("  No picks yet.")

    return "\n".join(lines)


async def generate_chat_response(
    user: User, draft: Draft, message: str, db: Session
) -> AIChatResponse:
    """AI chat assistant that helps users choose tickets."""
    if not settings.anthropic_api_key:
        return AIChatResponse(
            response="AI features require an Anthropic API key. Please configure ANTHROPIC_API_KEY.",
            suggested_picks=None,
        )

    client = _get_client()
    context = _build_draft_context(draft, db, user)

    system_prompt = (
        "You are a fun, knowledgeable Red Sox ticket draft assistant. "
        "You help users decide which games to pick based on their preferences. "
        "Consider factors like: opponent strength, weekend/holiday games, "
        "weather (early season = cold), rivalry games (Yankees!), "
        "and what games the user has already picked. "
        "Be enthusiastic about baseball and the Red Sox. "
        "When suggesting games, reference them by their Game ID so the user can easily pick them. "
        "Keep responses concise and actionable."
    )

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Here's the current draft state:\n\n{context}\n\nUser question: {message}",
            }
        ],
    )

    response_text = response.content[0].text

    # Try to extract suggested game IDs from the response
    import re
    game_ids = [int(x) for x in re.findall(r"Game (\d+)", response_text)]

    return AIChatResponse(
        response=response_text,
        suggested_picks=game_ids if game_ids else None,
    )


async def generate_weekly_summary(draft: Draft, db: Session) -> str:
    """Generate a funny AI weekly summary of draft activity."""
    if not settings.anthropic_api_key:
        return "AI features require an Anthropic API key. Please configure ANTHROPIC_API_KEY."

    client = _get_client()
    context = _build_draft_context(draft, db)

    # Get recent picks for the summary
    recent_picks = (
        db.query(Pick)
        .filter(Pick.draft_id == draft.id)
        .order_by(Pick.picked_at.desc())
        .limit(20)
        .all()
    )

    picks_text = []
    for pk in recent_picks:
        game = db.query(Game).filter(Game.id == pk.game_id).first()
        user = db.query(User).filter(User.id == pk.user_id).first()
        picks_text.append(
            f"  {user.display_name} picked {game.game_date.strftime('%a %b %d')} vs {game.opponent}"
        )

    system_prompt = (
        "You are a witty, irreverent sports columnist writing a weekly recap "
        "of a Red Sox ticket draft among friends. Be funny, roast people's picks "
        "(good-naturedly), point out trends, and add baseball commentary. "
        "Think Bill Simmons meets a fantasy football recap. Keep it to 2-3 paragraphs. "
        "Use the participants' actual names."
    )

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Draft state:\n{context}\n\n"
                    f"Recent picks:\n" + "\n".join(picks_text)
                ),
            }
        ],
    )

    return response.content[0].text
