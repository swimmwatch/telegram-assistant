"""
Authorization models.
"""
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from core.models.utils.mixins import TimedMixin
from infrastructure.db.base import Base


class IssuedToken(TimedMixin, Base):
    __tablename__ = "auth_issued_tokens"

    DEVICE_ID_LEN = 255

    id = orm.mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = orm.mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_id = orm.mapped_column(sa.String(length=DEVICE_ID_LEN), nullable=False)
    revoked = orm.mapped_column(sa.Boolean, default=False, nullable=False)
    expired_at = orm.mapped_column(sa.DateTime(timezone=True), nullable=False)

    user = orm.relationship("User", lazy="joined")


class PasswordResetCode(TimedMixin, Base):
    __tablename__ = "auth_password_reset_codes"

    CODE_LEN = 32

    id = orm.mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = orm.mapped_column(sa.String(CODE_LEN), unique=True, index=True)
    user_id = orm.mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expired_at = orm.mapped_column(sa.DateTime(timezone=True), nullable=False)
    activated_at = orm.mapped_column(sa.DateTime(timezone=True))

    user = orm.relationship("User", lazy="joined")
