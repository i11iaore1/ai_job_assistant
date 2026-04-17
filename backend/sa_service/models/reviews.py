from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Annotated

from sqlalchemy import JSON, ForeignKey, Text
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sa_service.models import Base, TimestampMixin

if TYPE_CHECKING:
    from sa_service.models import UserModel


jsonb_list = Annotated[
    list[str],
    mapped_column(JSON().with_variant(JSONB, "postgresql")),
]


class ReviewRequestStatus(Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReviewRequestModel(Base, TimestampMixin):
    __tablename__ = "review_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    raw_description: Mapped[str] = mapped_column(Text)
    comment: Mapped[str] = mapped_column(Text)
    status: Mapped[ReviewRequestStatus] = mapped_column(
        SA_Enum(
            ReviewRequestStatus,
            name="review_request_status",
        ),
        default=ReviewRequestStatus.PROCESSING,
    )

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="requests")

    review: Mapped["ReviewModel"] = relationship(
        "ReviewModel", back_populates="request", uselist=False
    )


class ReviewModel(Base, TimestampMixin):
    __tablename__ = "reviews"

    request_id: Mapped[int] = mapped_column(
        ForeignKey("review_requests.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[str]
    company_name: Mapped[str]
    advantages: Mapped[jsonb_list]
    disadvantages: Mapped[jsonb_list]
    questions: Mapped[jsonb_list]

    request: Mapped["ReviewRequestModel"] = relationship(
        "ReviewRequestModel", back_populates="review"
    )
