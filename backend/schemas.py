from pydantic import BaseModel

from datetime import date


# user
class UserInfoSchema(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    user_created_at: date
    user_updated_at: date


class UserProfileInfoSchema(BaseModel):
    resume_file_path: str
    resume_text: str
    context: str
    profile_created_at: date
    profile_updated_at: date


# review


class ReviewSchema(BaseModel):
    position: str | None
    company_name: str | None
    advantages: list[str]
    disadvantages: list[str]
    questions: list[str]
