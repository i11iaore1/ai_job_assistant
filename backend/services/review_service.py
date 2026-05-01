import asyncio
from typing import Any, AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import JSONServerSentEvent

from sa.models.reviews import ReviewRequestModel, ReviewRequestStatus
from sa.models.users import UserProfileModel
from sa.repositories import review_repository, review_request_repository
from serializers.reviews import ReviewDBSchema
from services.llm_service import llm_client


class ReviewJSONServerSentEvent(JSONServerSentEvent):
    def __init__(self, data: Any | None = None, *args, **kwargs) -> None:
        super().__init__(data, event="review_update", *args, **kwargs)


async def review_event_generator(
    request: Request,
    user_id: int,
    session: AsyncSession,
    review_request_id: int,
) -> AsyncGenerator[JSONServerSentEvent, None]:
    while True:
        if await request.is_disconnected():
            break

        session.expire_all()

        review_request = await review_request_repository.get_by_id_with_review(
            id=review_request_id,
            session=session,
        )

        if review_request is None or review_request.user_id != user_id:
            yield ReviewJSONServerSentEvent(data={"error": "Not found"})
            break

        match review_request.status:
            case ReviewRequestStatus.COMPLETED:
                review = ReviewDBSchema.model_validate(review_request.review)

                yield ReviewJSONServerSentEvent(
                    data={
                        "status": "completed",
                        "result": review.model_dump(mode="json"),
                    }
                )
                break

            case ReviewRequestStatus.FAILED:
                yield ReviewJSONServerSentEvent(data={"status": "failed"})
                break
            case ReviewRequestStatus.PROCESSING:
                pass

        await asyncio.sleep(2)


async def evaluate_in_the_background(
    session: AsyncSession,
    profile: UserProfileModel,
    review_request: ReviewRequestModel,
):
    try:
        result = await llm_client.evaluate_vacancy(
            resume_text=profile.resume_text,
            context=profile.context,
            vacancy_description=review_request.raw_description,
        )
    except Exception:
        review_request.fail()
        await session.commit()
        raise

    await review_repository.create(
        session=session,
        request=review_request,
        data=result.model_dump(),
    )
    await session.commit()
