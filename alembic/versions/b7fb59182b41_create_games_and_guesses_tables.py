"""create games and guesses tables

Revision ID: b7fb59182b41
Revises: eb064c798ed5
Create Date: 2026-06-26 11:43:18.853426

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7fb59182b41"
down_revision: Union[str, Sequence[str], None] = "eb064c798ed5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "games",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("word_to_guess", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
    )

    op.create_table(
        "guesses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("game_id", sa.Integer, sa.ForeignKey("games.id"), nullable=False),
        sa.Column("attempt_no", sa.Integer, nullable=False),
        sa.Column("guess_word", sa.String(length=50), nullable=False),
        sa.Column("feedback", sa.String(length=50), nullable=False),
        sa.UniqueConstraint("game_id", "attempt_no", name="uix_game_attempt"),
    )


def downgrade() -> None:
    op.drop_table("guesses")
    op.drop_table("games")
