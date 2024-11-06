"""
Models mixins.
"""
import sqlalchemy as sa
from sqlalchemy import orm

from infrastructure.db.base import Base


class TimedMixin(Base):
    __abstract__ = True

    created_at = orm.mapped_column(
        sa.DateTime(timezone=True),
        default=sa.func.now(),
        server_default=sa.func.now(),
        nullable=False,
    )
    updated_at = orm.mapped_column(
        sa.DateTime(timezone=True),
        default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )
