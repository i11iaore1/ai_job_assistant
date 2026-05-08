from fastapi import APIRouter, BackgroundTasks, Query, Request
from fastapi_pagination import Page
from sse_starlette import EventSourceResponse

from dependencies.auth import AccessDep, UserFromAccessDep
from dependencies.pagination import PaginationParams
from sa.database import AsyncSessionDependency
from sa.repositories import review_request_repository
from serializers.reviews import (
    FullReviewRequestSchema,
    ReviewDBSchema,
    ReviewRequestDBSchema,
    ReviewVacancySerializer,
    UpdateReviewSchema,
)
from services.review_service import (
    create_review_request,
    delete_review_request,
    evaluate_in_the_background,
    review_event_generator,
    update_review_result,
)

router = APIRouter()


@router.post("/reviews", response_model=ReviewRequestDBSchema, status_code=201)
async def request_vacancy_review(
    payload: ReviewVacancySerializer,
    background_tasks: BackgroundTasks,
    current_user: UserFromAccessDep,
    session: AsyncSessionDependency,
):
    new_review_request = await create_review_request(
        data=payload.model_dump(),
        user=current_user,
        session=session,
    )

    await session.commit()

    background_tasks.add_task(
        evaluate_in_the_background,
        session=session,
        profile=current_user.profile,
        review_request=new_review_request,
    )

    return new_review_request


@router.get("/reviews", response_model=Page[FullReviewRequestSchema])
async def list_review_requests(
    access: AccessDep,
    pagination_params: PaginationParams,
    session: AsyncSessionDependency,
    search: str | None = Query(None),
):
    return await review_request_repository.get_list(
        session=session,
        user_id=access.subject,
        params=pagination_params,
        search=search,
    )


@router.get("/reviews/{review_request_id}")
async def stream_review_status(
    request: Request,
    access: AccessDep,
    review_request_id: int,
    session: AsyncSessionDependency,
):
    stream = review_event_generator(
        request=request,
        user_id=access.subject,
        session=session,
        review_request_id=review_request_id,
    )

    return EventSourceResponse(stream, ping=15)


@router.patch("/reviews/{review_request_id}", response_model=ReviewDBSchema)
async def update_review(
    review_request_id: int,
    payload: UpdateReviewSchema,
    access: AccessDep,
    session: AsyncSessionDependency,
):
    review = await update_review_result(
        review_request_id=review_request_id,
        data_to_update=payload.model_dump(exclude_unset=True),
        user_id=access.subject,
        session=session,
    )
    await session.commit()
    return review


@router.delete("/reviews/{review_request_id}", status_code=204)
async def delete_review(
    review_request_id: int,
    access: AccessDep,
    session: AsyncSessionDependency,
):
    await delete_review_request(
        review_request_id=review_request_id,
        user_id=access.subject,
        session=session,
    )
    await session.commit()
    return None
