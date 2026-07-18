"""add_recommendation_models

Revision ID: ceda3e41fbdc
Revises: ed79141a0d00
Create Date: 2026-07-18 20:25:29.995744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ceda3e41fbdc'
down_revision: Union[str, Sequence[str], None] = 'ed79141a0d00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_preference_profiles",
        sa.Column("user_id", sa.String(length=100), primary_key=True, nullable=False),
        sa.Column("genre_weights", sa.JSON(), nullable=False),
        sa.Column("favorite_directors", sa.JSON(), nullable=False),
        sa.Column("favorite_actors", sa.JSON(), nullable=False),
        sa.Column("excluded_keywords", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False)
    )
    op.create_table(
        "user_interaction_histories",
        sa.Column("id", sa.String(length=100), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("interaction_type", sa.String(length=50), nullable=False),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("duration_watched_sec", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False)
    )
    op.create_index(
        "idx_user_interaction_user_id",
        "user_interaction_histories",
        ["user_id"]
    )
    op.create_index(
        "idx_user_interaction_movie_id",
        "user_interaction_histories",
        ["movie_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_user_interaction_movie_id", table_name="user_interaction_histories")
    op.drop_index("idx_user_interaction_user_id", table_name="user_interaction_histories")
    op.drop_table("user_interaction_histories")
    op.drop_table("user_preference_profiles")
