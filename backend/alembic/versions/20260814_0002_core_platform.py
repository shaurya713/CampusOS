"""create CampusOS core platform tables

Revision ID: 20260814_0002
Revises: 20260814_0001
Create Date: 2026-08-14
"""
from alembic import op
from app.db.base import Base

revision = "20260814_0002"
down_revision = "20260814_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    for table in ("announcements", "lost_found_items", "notifications", "complaint_comments", "complaint_status_history", "complaint_ai_analysis", "complaints", "staff_profiles", "categories", "departments"):
        Base.metadata.tables[table].drop(bind=op.get_bind(), checkfirst=True)
