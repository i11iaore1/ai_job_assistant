from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sa_service.models import BaseModel
from utils.security.password import hash_password, verify_password

if TYPE_CHECKING:
    from sa_service.models import ReviewRequestModel


class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    _password_hash: Mapped[str] = mapped_column(name="password_hash")
    username: Mapped[str]
    is_admin: Mapped[bool]

    profile: Mapped["UserProfileModel"] = relationship(
        "UserProfileModel", back_populates="user", uselist=False
    )

    requests: Mapped[list["ReviewRequestModel"]] = relationship(
        "ReviewRequestModel", back_populates="user"
    )

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password_to_set: str):
        self._password_hash = hash_password(password_to_set)

    def verify_password(self, password_to_verify: str) -> bool:
        return verify_password(password_to_verify, self._password_hash)


class UserProfileModel(BaseModel):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    resume_file_path: Mapped[str]
    resume_text: Mapped[str] = mapped_column(Text)
    context: Mapped[str] = mapped_column(Text)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")
