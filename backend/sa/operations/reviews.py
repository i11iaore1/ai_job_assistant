from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from sa.models.reviews import ReviewModel, ReviewRequestModel
from serializers.reviews import ReviewSchema, ReviewVacancySerializer


async def create_review_request(
    session: AsyncSession, user_id: int, request_info: ReviewVacancySerializer
) -> ReviewRequestModel:
    new_request = ReviewRequestModel(
        user_id=user_id,
        **request_info.model_dump(),
    )
    session.add(new_request)
    await session.flush()
    return new_request


async def get_review_request_by_id(
    session: AsyncSession,
    request_id: int,
    with_review: bool = False,
) -> ReviewRequestModel | None:
    query = select(ReviewRequestModel).filter(ReviewRequestModel.id == request_id)
    if with_review:
        query = query.options(joinedload(ReviewRequestModel.review))
    result = await session.execute(query)
    return result.scalars().first()


async def create_review(
    session: AsyncSession,
    request: ReviewRequestModel,
    review_info: ReviewSchema,
) -> ReviewModel:
    new_review = ReviewModel(
        request_id=request.id,
        **review_info.model_dump(),
    )
    session.add(new_review)
    request.complete()
    await session.flush()
    await session.refresh(request)
    return request.review
