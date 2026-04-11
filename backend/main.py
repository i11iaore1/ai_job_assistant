import uvicorn
from fastapi import FastAPI

from serializers.reviews import ReviewVacancyResponseSerializer, ReviewVacancySerializer
from serializers.users import (
    LoginResponseSerializer,
    LoginSerializer,
    RegistrationResponseSerializer,
    RegistrationSerializer,
)

app = FastAPI()


@app.post("/register")
def register(
    payload: RegistrationSerializer,
) -> RegistrationResponseSerializer:
    # create user if email is unique
    # create JWT-token with users id in payload
    # set cookies depending on remember_me
    # return user info + cookies
    pass


@app.post("/login")
def login(payload: LoginSerializer) -> LoginResponseSerializer:
    # check if payload info is correct
    # if join returns null in profile.user_id, set profile_info to null in response
    # create JWT-token with users id in payload
    # set cookies depending on remember_me
    # return user+profile info + cookies
    pass


# review


@app.post("/review")
def review_vacancy(payload: ReviewVacancySerializer) -> ReviewVacancyResponseSerializer:
    # resume_text = "Skills: Python, Django, JavaScript"
    # context = "Looking for a first remote fulltime job. I have no experience yet"

    # result = llm_client.evaluate_vacancy(
    #     resume_text=resume_text,
    #     context=context,
    #     vacancy_description=payload.vacancy_description,
    # )

    # return result
    pass


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
