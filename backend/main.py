import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from llm_service import llm_client
from schemas import UserInfoSchema, UserProfileInfoSchema, ReviewSchema


app = FastAPI()


class RegistrationPayloadSchema(BaseModel):
    email: str
    password: str
    remember_me: bool  # determines whether refresh is sent as Session Cookie or Long living (Max-Age: 2592000)


@app.post("/register")
def register(
    payload: RegistrationPayloadSchema,
) -> UserInfoSchema:  # user does not have a profile yet
    # create user if email is unique
    # create JWT-token with users id in payload
    # set cookies depending on remember_me
    # return user info + cookies
    pass


class LoginPayloadSchema(BaseModel):
    email: str
    password: str
    remember_me: bool


class LoginResponseSchema(UserInfoSchema):
    # user might not have a profile yet
    profile_info: UserProfileInfoSchema | None


@app.post("/login")
def login(payload: LoginPayloadSchema) -> LoginResponseSchema:
    # check if payload info is correct
    # if join returns null in profile.user_id, set profile_info to null in response
    # create JWT-token with users id in payload
    # set cookies depending on remember_me
    # return user+profile info + cookies
    pass


# review


class ReviewPayloadSchema(BaseModel):
    vacancy_description: str


@app.post("/review")
def review_vacancy(payload: ReviewPayloadSchema) -> ReviewSchema:
    resume_text = "Skills: Python, Django, JavaScript"
    context = "Looking for a first remote fulltime job. I have no experience yet"

    result = llm_client.evaluate_vacancy(
        resume_text=resume_text,
        context=context,
        vacancy_description=payload.vacancy_description,
    )

    return result


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
