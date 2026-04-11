"""add_updated_at_trigger

Revision ID: 4c30af97f2a2
Revises: 50dd288e399c
Create Date: 2026-04-11 20:20:16.237518

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

from sa_service.update_trigger import (
    create_on_update_trigger,
    create_on_update_trigger_func,
    drop_on_update_trigger,
    drop_on_update_trigger_func,
    trigger_name,
)

# revision identifiers, used by Alembic.
revision: str = "4c30af97f2a2"
down_revision: Union[str, Sequence[str], None] = "50dd288e399c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tables_with_trigger = [
    "users",
    "user_profiles",
    "review_requests",
    "reviews",
]


def upgrade() -> None:
    op.execute(text(create_on_update_trigger_func))

    for table_name in tables_with_trigger:
        op.execute(
            text(
                create_on_update_trigger(
                    trigger_name=trigger_name(table_name),  # singular form
                    table_name=table_name,  # plural form
                )
            )
        )


def downgrade() -> None:
    op.execute(text(drop_on_update_trigger_func))

    for table_name in tables_with_trigger:
        op.execute(
            text(
                drop_on_update_trigger(
                    trigger_name=trigger_name(table_name),  # singular form
                    table_name=table_name,  # plural form
                )
            )
        )
