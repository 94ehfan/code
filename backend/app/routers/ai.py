from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Draft, User
from app.schemas import AIChatMessage, AIChatResponse, WeeklySummaryResponse
from app.services.ai_service import generate_chat_response, generate_weekly_summary

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_model=AIChatResponse)
async def chat_with_ai(
    message: AIChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == message.draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    response = await generate_chat_response(
        user=current_user,
        draft=draft,
        message=message.message,
        db=db,
    )
    return response


@router.get("/summary/{draft_id}", response_model=WeeklySummaryResponse)
async def get_weekly_summary(
    draft_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    summary = await generate_weekly_summary(draft, db)
    return WeeklySummaryResponse(summary=summary, generated_at=datetime.utcnow())
