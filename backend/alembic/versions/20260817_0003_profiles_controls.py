"""add identity, expertise, attachments, and controls

Revision ID: 20260817_0003
Revises: 20260814_0002
"""
from alembic import op
import sqlalchemy as sa

revision = "20260817_0003"
down_revision = "20260814_0002"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("users", sa.Column("profile_photo_url", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("government_id", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("permanent_address", sa.String(500), nullable=True))
    op.create_unique_constraint("uq_users_government_id", "users", ["government_id"])
    op.add_column("staff_profiles", sa.Column("experience_years", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("staff_profiles", sa.Column("working_hours", sa.String(120), nullable=True))
    op.add_column("complaints", sa.Column("image_url", sa.String(500), nullable=True))
    op.add_column("complaints", sa.Column("video_url", sa.String(500), nullable=True))

def downgrade() -> None:
    op.drop_column("complaints", "video_url")
    op.drop_column("complaints", "image_url")
    op.drop_column("staff_profiles", "working_hours")
    op.drop_column("staff_profiles", "experience_years")
    op.drop_constraint("uq_users_government_id", "users", type_="unique")
    op.drop_column("users", "permanent_address")
    op.drop_column("users", "government_id")
    op.drop_column("users", "profile_photo_url")
