from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import ai, drafts, picks, users
from app.websocket import websocket_endpoint

app = FastAPI(
    title=settings.app_name,
    description=(
        "A web app for managing Red Sox ticket drafts among friends. "
        "Supports real-time draft picks, SMS notifications, AI-powered "
        "chat assistance, and an agent-friendly API for AI integrations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (in production, use Alembic migrations instead)
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(users.router)
app.include_router(drafts.router)
app.include_router(picks.router)
app.include_router(ai.router)

# WebSocket endpoint
app.websocket("/ws/draft/{draft_id}")(websocket_endpoint)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
