from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Draft, DraftParticipant, DraftStatus, Game, Pick, User
from app.schemas import (
    DraftCreate,
    DraftDetail,
    DraftResponse,
    GameCreate,
    GameResponse,
    ParticipantAdd,
    ParticipantResponse,
    PickResponse,
)

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


@router.post("/", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
def create_draft(
    draft_in: DraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = Draft(
        name=draft_in.name,
        season_year=draft_in.season_year,
        snake_draft=draft_in.snake_draft,
        seats_per_game=draft_in.seats_per_game,
        created_by_id=current_user.id,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.get("/", response_model=list[DraftResponse])
def list_drafts(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return db.query(Draft).all()


@router.get("/{draft_id}", response_model=DraftDetail)
def get_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    # Compute seats_available for each game
    for game in draft.games:
        taken = db.query(Pick).filter(
            Pick.draft_id == draft_id, Pick.game_id == game.id
        ).count()
        game.seats_available = draft.seats_per_game - taken

    return draft


@router.post("/{draft_id}/participants", response_model=ParticipantResponse)
def add_participant(
    draft_id: int,
    participant: ParticipantAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the commissioner can add participants")
    if draft.status != DraftStatus.SETUP:
        raise HTTPException(status_code=400, detail="Can only add participants during setup")

    dp = DraftParticipant(
        draft_id=draft_id,
        user_id=participant.user_id,
        draft_order=participant.draft_order,
    )
    db.add(dp)
    db.commit()
    db.refresh(dp)
    return dp


@router.post("/{draft_id}/games", response_model=GameResponse)
def add_game(
    draft_id: int,
    game_in: GameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the commissioner can add games")

    game = Game(draft_id=draft_id, **game_in.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    game.seats_available = draft.seats_per_game
    return game


@router.post("/{draft_id}/games/bulk", response_model=list[GameResponse])
def add_games_bulk(
    draft_id: int,
    games_in: list[GameCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the commissioner can add games")

    games = []
    for g in games_in:
        game = Game(draft_id=draft_id, **g.model_dump())
        db.add(game)
        games.append(game)
    db.commit()
    for game in games:
        db.refresh(game)
        game.seats_available = draft.seats_per_game
    return games


@router.post("/{draft_id}/start", response_model=DraftResponse)
def start_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the commissioner can start the draft")
    if draft.status != DraftStatus.SETUP:
        raise HTTPException(status_code=400, detail="Draft is not in setup status")
    if len(draft.participants) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 participants")
    if len(draft.games) < 1:
        raise HTTPException(status_code=400, detail="Need at least 1 game")

    draft.status = DraftStatus.ACTIVE
    draft.started_at = datetime.utcnow()
    draft.current_round = 1
    draft.current_pick_index = 0
    db.commit()
    db.refresh(draft)

    # Notify first picker
    from app.services.notification_service import notify_turn

    first_participant = (
        db.query(DraftParticipant)
        .filter(DraftParticipant.draft_id == draft_id, DraftParticipant.draft_order == 1)
        .first()
    )
    if first_participant:
        notify_turn(first_participant.user, draft)

    return draft


@router.post("/{draft_id}/pause", response_model=DraftResponse)
def pause_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the commissioner can pause")
    draft.status = DraftStatus.PAUSED
    db.commit()
    db.refresh(draft)
    return draft


@router.post("/{draft_id}/resume", response_model=DraftResponse)
def resume_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the commissioner can resume")
    if draft.status != DraftStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Draft is not paused")
    draft.status = DraftStatus.ACTIVE
    db.commit()
    db.refresh(draft)
    return draft
