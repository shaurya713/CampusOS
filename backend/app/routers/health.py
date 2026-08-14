from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.db.database import SessionLocal

router = APIRouter(tags=["System"])


@router.get("/health", summary="Service health check")
def health_check():
    database = "unavailable"
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        pass
    return {"status": "ok" if database == "ok" else "degraded", "database": database, "environment": get_settings().environment}

