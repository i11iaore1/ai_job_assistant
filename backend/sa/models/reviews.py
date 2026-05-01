from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Annotated

from sqlalchemy import JSON, ForeignKey, Index, Text, text
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sa.models import Base, TimestampMixin

if TYPE_CHECKING:
    from sa.models import UserModel


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
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
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
        "ReviewModel",
        back_populates="request",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True,
    )

    def fail(self):
        self.status = ReviewRequestStatus.FAILED

    def complete(self):
        self.status = ReviewRequestStatus.COMPLETED


class ReviewModel(Base, TimestampMixin):
    __tablename__ = "reviews"
    __table_args__ = (
        Index(
            "ix_reviews_advantages_trgm",
            text("(advantages::text) gin_trgm_ops"),
            postgresql_using="gin",
        ),
        Index(
            "ix_reviews_disadvantages_trgm",
            text("(disadvantages::text) gin_trgm_ops"),
            postgresql_using="gin",
        ),
        Index(
            "ix_reviews_questions_trgm",
            text("(questions::text) gin_trgm_ops"),
            postgresql_using="gin",
        ),
    )

    request_id: Mapped[int] = mapped_column(
        ForeignKey("review_requests.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[str | None]
    company_name: Mapped[str | None]
    advantages: Mapped[jsonb_list]
    disadvantages: Mapped[jsonb_list]
    questions: Mapped[jsonb_list]

    request: Mapped["ReviewRequestModel"] = relationship(
        "ReviewRequestModel", back_populates="review"
    )
