from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Draft, DraftParticipant, DraftStatus, Game, Pick


def get_current_picker(draft: Draft, db: Session) -> int | None:
    """Return the user_id of whoever should pick next."""
    if draft.status != DraftStatus.ACTIVE:
        return None

    participants = (
        db.query(DraftParticipant)
        .filter(DraftParticipant.draft_id == draft.id)
        .order_by(DraftParticipant.draft_order)
        .all()
    )
    if not participants:
        return None

    n = len(participants)
    pick_index = draft.current_pick_index

    if draft.snake_draft:
        # Snake draft: 1,2,3,...,n,n,...,3,2,1,1,2,3,...
        cycle = 2 * n
        pos = pick_index % cycle
        if pos < n:
            order_index = pos
        else:
            order_index = cycle - 1 - pos
    else:
        order_index = pick_index % n

    return participants[order_index].user_id


def get_current_round(draft: Draft) -> int:
    """Calculate the current round number."""
    participants_count = len(draft.participants)
    if participants_count == 0:
        return 1
    return (draft.current_pick_index // participants_count) + 1


def advance_draft(draft: Draft, db: Session):
    """Move to the next pick in the draft."""
    draft.current_pick_index += 1
    draft.current_round = get_current_round(draft)

    # Check if draft is complete (all seats for all games taken)
    total_seats = len(draft.games) * draft.seats_per_game
    total_picks = db.query(Pick).filter(Pick.draft_id == draft.id).count()

    if total_picks >= total_seats:
        draft.status = DraftStatus.COMPLETED
        draft.completed_at = datetime.utcnow()
        db.commit()
        return

    db.commit()

    # Notify next picker
    next_picker_id = get_current_picker(draft, db)
    if next_picker_id:
        from app.models import User

        next_user = db.query(User).filter(User.id == next_picker_id).first()
        if next_user:
            from app.services.notification_service import notify_turn
            from app.websocket import broadcast_draft_update

            notify_turn(next_user, draft)
            broadcast_draft_update(draft.id, {
                "type": "pick_made",
                "current_picker_id": next_picker_id,
                "current_round": draft.current_round,
                "current_pick_index": draft.current_pick_index,
            })


def get_available_games(draft: Draft, db: Session) -> list[Game]:
    """Return games that still have at least one seat available."""
    games = db.query(Game).filter(Game.draft_id == draft.id).all()
    available = []
    for game in games:
        taken = (
            db.query(Pick)
            .filter(Pick.draft_id == draft.id, Pick.game_id == game.id)
            .count()
        )
        if taken < draft.seats_per_game:
            game.seats_available = draft.seats_per_game - taken
            available.append(game)
    return available
