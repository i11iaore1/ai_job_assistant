import uvicorn
from fastapi import FastAPI, HTTPException, Response

from sa_service.database import AsyncSessionDependency
from sa_service.operations.users import (
    EmailExists,
    create_user,
    get_user_by_email,
    get_users,
)
from serializers.users import (
    CreateUserSchema,
    LoginResponseSerializer,
    LoginSerializer,
    RegistrationResponseSerializer,
    RegistrationSerializer,
)

app = FastAPI()


@app.get("/users", response_model=list[RegistrationResponseSerializer])
async def get_user_list(
    session: AsyncSessionDependency,
) -> list[RegistrationResponseSerializer]:
    users = await get_users(session=session)

    user_dto_list = [
        RegistrationResponseSerializer.model_validate(user, from_attributes=True)
        for user in users
    ]

    return user_dto_list


@app.post("/register", response_model=RegistrationResponseSerializer)
async def register(
    payload: RegistrationSerializer,
    session: AsyncSessionDependency,
    response: Response,
) -> RegistrationResponseSerializer:
    user_info = CreateUserSchema(**payload.model_dump())

    try:
        new_user = await create_user(session=session, user_info=user_info)
    except EmailExists:
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )

    return RegistrationResponseSerializer.model_validate(new_user, from_attributes=True)
    # create JWT-token with users id in payload
    # set cookies depending on remember_me


@app.post("/login", response_model=LoginResponseSerializer)
async def login(
    payload: LoginSerializer,
    session: AsyncSessionDependency,
    response: Response,
) -> LoginResponseSerializer:
    user = await get_user_by_email(
        session=session, email=payload.email, with_profile=True
    )
    if user and user.verify_password(payload.password):
        return LoginResponseSerializer.model_validate(user, from_attributes=True)

    raise HTTPException(status_code=401, detail="Wrong email or password.")

    # create JWT-token with users id in payload
    # set cookies depending on remember_me


# review


# @app.post("/review")
# def review_vacancy(payload: ReviewVacancySerializer) -> ReviewVacancyResponseSerializer:
#     # resume_text = "Skills: Python, Django, JavaScript"
#     # context = "Looking for a first remote fulltime job. I have no experience yet"

#     # result = llm_client.evaluate_vacancy(
#     #     resume_text=resume_text,
#     #     context=context,
#     #     vacancy_description=payload.vacancy_description,
#     # )

#     # return result
#     pass


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
