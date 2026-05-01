from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sa.models import Base, TimestampMixin
from utils.security.password import hash_password, verify_password

if TYPE_CHECKING:
    from sa.models import ReviewRequestModel


class UserModel(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    _password_hash: Mapped[str] = mapped_column(name="password_hash")
    username: Mapped[str]
    is_admin: Mapped[bool]

    profile: Mapped["UserProfileModel"] = relationship(
        "UserProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True,
    )

    requests: Mapped[list["ReviewRequestModel"]] = relationship(
        "ReviewRequestModel",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True,
    )

    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        "RefreshTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True,
    )

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password_to_set: str):
        self._password_hash = hash_password(password_to_set)

    def verify_password(self, password_to_verify: str) -> bool:
        return verify_password(password_to_verify, self._password_hash)


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    jti: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="refresh_tokens"
    )


class UserProfileModel(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    resume_file_path: Mapped[str]
    resume_text: Mapped[str] = mapped_column(Text)
    context: Mapped[str] = mapped_column(Text)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")
