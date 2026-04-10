from datetime import datetime
from enum import Enum
from typing import Annotated

from sqlalchemy import JSON, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


int_pk = Annotated[int, mapped_column(primary_key=True)]
json_list = Annotated[
    list[str],
    mapped_column(JSON().with_variant(JSONB, "postgresql")),
]


class BaseModel(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )


class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[int_pk]
    email: Mapped[str]  # email
    password_hash: Mapped[str] = mapped_column()  # password
    username: Mapped[str]
    is_admin: Mapped[bool]


class UserProfileModel(BaseModel):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    resume_file_path: Mapped[str]
    resume_text: Mapped[str]
    context: Mapped[str]


class ReviewRequestStatus(Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReviewRequest(BaseModel):
    __tablename__ = "review_requests"

    id: Mapped[int_pk]
    user_id: Mapped[int]
    raw_description: Mapped[str]
    comment: Mapped[str]
    status: Mapped[ReviewRequestStatus]


class ReviewResult(BaseModel):
    __tablename__ = "review_results"

    request_id: Mapped[int] = mapped_column(
        ForeignKey("review_requests.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[str]
    company_name: Mapped[str]
    advantages: Mapped[json_list]
    disadvantages: Mapped[json_list]
    questions: Mapped[json_list]
