from fastapi import APIRouter, BackgroundTasks, Query, Request
from fastapi_pagination import Page
from sse_starlette import EventSourceResponse

from dependencies.auth import FullUserFromAccessDependency, UserFromAccessDependency
from dependencies.pagination import PaginationParams
from sa.database import AsyncSessionDependency
from sa.operations.reviews import create_review_request, get_review_requests
from serializers.reviews import (
    FullReviewRequestSchema,
    ReviewRequestDBSchema,
    ReviewVacancySerializer,
)
from services.review_service import evaluate_in_the_background, review_event_generator

router = APIRouter()


@router.post("/review-request", response_model=ReviewRequestDBSchema)
async def request_vacancy_review(
    session: AsyncSessionDependency,
    payload: ReviewVacancySerializer,
    current_user: FullUserFromAccessDependency,
    background_tasks: BackgroundTasks,
):
    new_review_request = await create_review_request(
        session=session,
        user_id=current_user.id,
        request_info=payload,
    )

    await session.commit()

    background_tasks.add_task(
        evaluate_in_the_background,
        session=session,
        profile=current_user.profile,
        review_request=new_review_request,
    )

    return new_review_request


@router.get("/review-request", response_model=Page[FullReviewRequestSchema])
async def list_review_requests(
    session: AsyncSessionDependency,
    current_user: UserFromAccessDependency,
    pagination_params: PaginationParams,
    search: str | None = Query(None),
):
    return await get_review_requests(
        session=session,
        user_id=current_user.id,
        params=pagination_params,
        search=search,
    )


@router.get("/review/{review_request_id}")
async def stream_review_status(
    request: Request,
    current_user: UserFromAccessDependency,
    review_request_id: int,
    session: AsyncSessionDependency,
):
    stream = review_event_generator(
        request=request,
        user_id=current_user.id,
        session=session,
        review_request_id=review_request_id,
    )

    return EventSourceResponse(stream, ping=15)
