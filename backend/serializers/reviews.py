from pydantic import BaseModel

from sa.models.reviews import ReviewRequestStatus
from serializers.base_serializer import BaseDatedSerializer

# DTOs


class ReviewRequestDBSchema(BaseDatedSerializer):
    """DTO for review_request DB record"""

    id: int
    raw_description: str
    comment: str
    status: ReviewRequestStatus


class ReviewSchema(BaseModel):
    """DTO for review"""

    position: str | None
    company_name: str | None
    advantages: list[str]
    disadvantages: list[str]
    questions: list[str]


class ReviewDBSchema(ReviewSchema, BaseDatedSerializer):
    """DTO for review  DB record"""

    pass


# review_vacancy


class ReviewVacancySerializer(BaseModel):
    """validates review vacancy request payload"""

    raw_description: str
    comment: str


class ReviewVacancyResponseSerializer(ReviewRequestDBSchema):
    """describes review vacancy response payload structure"""

    review: ReviewDBSchema | None
