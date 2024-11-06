import sqlalchemy as sa
from sqlalchemy import orm

from infrastructure.db.base import Base

from .utils.mixins import TimedMixin


class User(TimedMixin, Base):
    __tablename__ = "users"

    id = orm.mapped_column(sa.Integer, primary_key=True)
    tg_id = orm.mapped_column(sa.Integer, unique=True, index=True)
    session = orm.mapped_column(sa.String, nullable=True, default=None)
