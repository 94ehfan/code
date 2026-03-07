from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Draft, DraftParticipant, DraftStatus, Game, Pick, User
from app.schemas import AgentPickRequest, DraftStateResponse, PickCreate, PickResponse
from app.services.draft_service import (
    get_available_games,
    get_current_picker,
    advance_draft,
)

router = APIRouter(prefix="/api/drafts/{draft_id}/picks", tags=["picks"])


@router.post("/", response_model=PickResponse)
def make_pick(
    draft_id: int,
    pick_in: PickCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.status != DraftStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Draft is not active")

    # Check it's this user's turn
    current_picker_id = get_current_picker(draft, db)
    if current_user.id != current_picker_id:
        raise HTTPException(status_code=403, detail="It's not your turn to pick")

    # Validate game exists and has seats
    game = db.query(Game).filter(Game.id == pick_in.game_id, Game.draft_id == draft_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found in this draft")

    existing_seats = (
        db.query(Pick)
        .filter(Pick.draft_id == draft_id, Pick.game_id == game.id)
        .count()
    )
    if existing_seats >= draft.seats_per_game:
        raise HTTPException(status_code=400, detail="No seats available for this game")

    # Auto-assign seat number
    seat_number = pick_in.seat_number
    if seat_number is None:
        seat_number = existing_seats + 1
    else:
        taken = (
            db.query(Pick)
            .filter(
                Pick.draft_id == draft_id,
                Pick.game_id == game.id,
                Pick.seat_number == seat_number,
            )
            .first()
        )
        if taken:
            raise HTTPException(status_code=400, detail=f"Seat {seat_number} already taken")

    # Calculate overall pick number
    total_picks = db.query(Pick).filter(Pick.draft_id == draft_id).count()

    pick = Pick(
        draft_id=draft_id,
        game_id=game.id,
        user_id=current_user.id,
        round_number=draft.current_round,
        pick_number=total_picks + 1,
        seat_number=seat_number,
    )
    db.add(pick)
    db.commit()
    db.refresh(pick)

    # Advance draft to next picker
    advance_draft(draft, db)

    return pick


@router.get("/", response_model=list[PickResponse])
def list_picks(
    draft_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return (
        db.query(Pick)
        .filter(Pick.draft_id == draft_id)
        .order_by(Pick.pick_number)
        .all()
    )


@router.get("/my", response_model=list[PickResponse])
def my_picks(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Pick)
        .filter(Pick.draft_id == draft_id, Pick.user_id == current_user.id)
        .order_by(Pick.pick_number)
        .all()
    )


# --- Agent-friendly endpoints ---
@router.get("/state", response_model=DraftStateResponse)
def get_draft_state(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get complete draft state — designed for AI agents to consume."""
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    available = get_available_games(draft, db)
    current_picker_id = get_current_picker(draft, db)
    current_picker = db.query(User).filter(User.id == current_picker_id).first()

    all_picks = (
        db.query(Pick)
        .filter(Pick.draft_id == draft_id)
        .order_by(Pick.pick_number)
        .all()
    )
    my_picks_list = [p for p in all_picks if p.user_id == current_user.id]

    return DraftStateResponse(
        draft=draft,
        participants=draft.participants,
        available_games=available,
        picks_made=all_picks,
        current_picker=current_picker,
        your_picks=my_picks_list,
    )


@router.post("/agent", response_model=PickResponse)
def agent_pick(
    draft_id: int,
    pick_in: AgentPickRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Make a pick on behalf of the authenticated user — designed for AI agents."""
    return make_pick(
        draft_id=draft_id,
        pick_in=PickCreate(game_id=pick_in.game_id, seat_number=pick_in.seat_number),
        db=db,
        current_user=current_user,
    )
