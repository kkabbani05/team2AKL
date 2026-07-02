"""add constraint to existing table

Revision ID: 7387ac24780d
Revises: b7fb59182b41
Create Date: 2026-06-29 14:07:00.368638

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7387ac24780d"
down_revision: Union[str, Sequence[str], None] = "b7fb59182b41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uix_user_word_to_guess",
        "games",
        ["user_id", "word_to_guess"],
    )


def downgrade() -> None:
    op.drop_constraint("uix_user_word_to_guess", "games", type_="unique")
