from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import String, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from sa.models import ReviewModel, ReviewRequestModel
from sa.repositories.base import BaseRepository


class ReviewRequestRepository(BaseRepository[ReviewRequestModel]):
    def __init__(self) -> None:
        super().__init__(
            model=ReviewRequestModel,
            updatable_fields={"raw_description", "comment"},
        )

    async def get_by_id_with_review(
        self,
        id: int,
        session: AsyncSession,
    ) -> ReviewRequestModel | None:
        query = (
            select(ReviewRequestModel)
            .filter(ReviewRequestModel.id == id)
            .options(joinedload(ReviewRequestModel.review))
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_list(
        self,
        user_id: int,
        params: Params,
        session: AsyncSession,
        search: str | None = None,
    ) -> Page[ReviewRequestModel]:
        query = (
            select(ReviewRequestModel)
            .filter(ReviewRequestModel.user_id == user_id)
            .options(joinedload(ReviewRequestModel.review))
        )

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                ReviewRequestModel.review.has(
                    or_(
                        cast(ReviewModel.advantages, String).ilike(search_term),
                        cast(ReviewModel.disadvantages, String).ilike(search_term),
                        cast(ReviewModel.questions, String).ilike(search_term),
                    )
                )
            )

        query = query.order_by(
            ReviewRequestModel.created_at.desc(),
            ReviewRequestModel.id.asc(),
        )

        return await paginate(session, query, params)


review_request_repository = ReviewRequestRepository()
