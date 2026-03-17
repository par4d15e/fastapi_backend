"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
# pyright: reportAttributeAccessIssue=none
from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
    # PostgreSQL 的 trigram 索引（gin_trgm_ops）需要 pg_trgm 扩展
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
    ${upgrades if upgrades else "pass"}



def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}