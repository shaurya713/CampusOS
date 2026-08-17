# CampusOS

CampusOS is an AI-powered college operations platform. It includes a FastAPI/PostgreSQL backend and a Next.js operations portal.

## Run with Docker

1. Copy `.env.example` to `.env` and replace `JWT_SECRET_KEY`.
2. Run `docker compose up --build` from this directory.
3. Open API documentation at `http://localhost:8000/docs`; service health is at `http://localhost:8000/api/v1/health`.

## Local backend

```bash
cd backend
cp .env.example .env
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Then seed local data:

```bash
python seed.py
```

Development credentials: `admin@campus.edu` / `CampusOS123`.

## Implemented endpoints

- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- Departments, categories, staff, complaints, comments, status/assignment, notifications, uploads, Lost & Found, announcements, and admin analytics are documented at `/docs`.
