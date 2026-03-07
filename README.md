# Red Sox Ticket Draft

A web app for managing Red Sox season ticket drafts among friends. Replaces the spreadsheet + group text workflow with a real-time draft board, SMS notifications, AI-powered pick assistance, and an agent-friendly API.

## Features

- **Real-time Draft Board** — See picks happen live via WebSocket updates
- **Snake Draft** — Configurable snake or linear draft order
- **SMS Notifications** — Twilio-powered alerts when it's your turn to pick
- **AI Draft Assistant** — Chat with an AI that knows the draft state and can recommend games
- **Weekly Recap** — AI-generated funny summaries of everyone's picks
- **Agent-Friendly API** — OpenAPI spec at `/docs` — any AI agent can authenticate and make picks
- **Mobile-First** — Responsive design that works great on phones

## Tech Stack

- **Frontend**: React + Vite + TypeScript
- **Backend**: Python + FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Real-time**: WebSockets
- **Notifications**: Twilio SMS
- **AI**: Anthropic Claude API
- **Deployment**: Docker + Azure

## Quick Start

### With Docker Compose

```sh
# Copy environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your keys (Twilio, Anthropic, etc.)

# Start everything
docker compose up --build
```

- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

**Backend:**
```sh
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Start PostgreSQL (e.g., via Docker)
uvicorn app.main:app --reload
```

**Frontend:**
```sh
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` and `/ws` to the backend at `localhost:8000`.

## API Overview

All endpoints require a Bearer token (obtained via `/api/users/login`).

| Endpoint | Description |
|---|---|
| `POST /api/users/register` | Create account |
| `POST /api/users/login` | Get auth token |
| `POST /api/drafts/` | Create a new draft |
| `POST /api/drafts/{id}/start` | Start the draft |
| `POST /api/drafts/{id}/picks/` | Make a pick |
| `GET /api/drafts/{id}/picks/state` | Full draft state (for AI agents) |
| `POST /api/drafts/{id}/picks/agent` | Agent-friendly pick endpoint |
| `POST /api/ai/chat` | Chat with AI assistant |
| `GET /api/ai/summary/{id}` | Get weekly AI recap |
| `WS /ws/draft/{id}` | Real-time draft updates |

Full OpenAPI spec available at `/docs`.

## AI Agent Integration

External AI agents can integrate by:

1. Authenticating via `/api/users/login` to get a Bearer token
2. Fetching draft state via `GET /api/drafts/{id}/picks/state`
3. Making picks via `POST /api/drafts/{id}/picks/agent`

The `/docs` endpoint provides a full OpenAPI 3.1 spec that agents can consume.

## Configuration

Set these environment variables (or use `backend/.env`):

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Twilio sender phone number |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI features |
| `APP_URL` | Public URL (used in SMS links) |
