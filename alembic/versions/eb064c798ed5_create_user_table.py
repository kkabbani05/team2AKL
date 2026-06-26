"""create user table

Revision ID: eb064c798ed5
Revises: 
Create Date: 2026-06-26 09:02:47.455175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb064c798ed5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    )""")
    pass


def downgrade() -> None:
    op.execute("""DROP TABLE users""")
    pass
