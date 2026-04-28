from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import String, cast, or_, select
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


async def get_review_requests(
    session: AsyncSession,
    user_id: int,
    params: Params,
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
