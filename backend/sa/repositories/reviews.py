from typing import Any, Mapping

from sqlalchemy.ext.asyncio import AsyncSession

from sa.models import ReviewModel, ReviewRequestModel
from sa.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[ReviewModel]):
    def __init__(self) -> None:
        super().__init__(
            model=ReviewModel,
            updatable_fields={
                "position",
                "company_name",
                "advantages",
                "disadvantages",
                "questions",
            },
        )

    async def create(
        self,
        session: AsyncSession,
        request: ReviewRequestModel,
        data: Mapping[str, Any],
    ) -> ReviewModel:
        new_review = ReviewModel(
            request_id=request.id,
            **data,
        )
        session.add(new_review)
        request.complete()
        await session.flush()
        await session.refresh(request)
        return request.review


review_repository = ReviewRepository()
