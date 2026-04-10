from pydantic import BaseModel

from llm_service.constants import NOT_MENTIONED
from schemas import ReviewSchema


class LLMReviewResultSchema(BaseModel):
    position: str  # if None allowed, model might bahave "lazy"
    company_name: str  # if None allowed, model might bahave "lazy"
    advantages: list[str]
    disadvantages: list[str]
    questions: list[str]

    def to_review(self) -> ReviewSchema:
        data = self.model_dump()
        for field in ["position", "company_name"]:
            if data[field] == NOT_MENTIONED:
                data[field] = None
        return ReviewSchema(**data)
