from pydantic import BaseModel


class ReviewResult(BaseModel):
    position: str
    company_name: str | None
    advantages: list[str]
    disadvantages: list[str]
    questions: list[str]
