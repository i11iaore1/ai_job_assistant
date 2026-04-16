import uvicorn
from fastapi import FastAPI, HTTPException, Response

from dependencies.auth import AccessUserDependency, RefreshUserDependency
from sa_service.database import AsyncSessionDependency
from sa_service.operations.users import (
    EmailExists,
    create_user,
    create_user_profile,
    get_user_by_email,
    get_users,
)
from serializers.users import (
    CreateUserProfileSchema,
    CreateUserSchema,
    FullUserInfoSchema,
    LoginSerializer,
    RegistrationSerializer,
    UserDBSchema,
    UserProfileDBSchema,
)
from utils.security.auth import (
    delete_token_cookies,
    set_token_cookies,
)

app = FastAPI()


@app.get("/users", response_model=list[UserDBSchema])
async def get_user_list(
    session: AsyncSessionDependency,
) -> list[UserDBSchema]:
    users = await get_users(session=session)

    user_dto_list = [
        UserDBSchema.model_validate(user, from_attributes=True) for user in users
    ]

    return user_dto_list


@app.post("/register", response_model=UserDBSchema)
async def register(
    payload: RegistrationSerializer,
    session: AsyncSessionDependency,
    response: Response,
) -> UserDBSchema:
    user_info = CreateUserSchema(**payload.model_dump())
    try:
        new_user = await create_user(session=session, user_info=user_info)
    except EmailExists:
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )
    new_user_dto = UserDBSchema.model_validate(new_user, from_attributes=True)
    set_token_cookies(
        user=new_user_dto, response=response, remember_me=payload.remember_me
    )
    return new_user_dto


@app.post("/login", response_model=FullUserInfoSchema)
async def login(
    payload: LoginSerializer,
    session: AsyncSessionDependency,
    response: Response,
) -> FullUserInfoSchema:
    user = await get_user_by_email(
        session=session, email=payload.email, with_profile=True
    )
    if user is None or not user.verify_password(payload.password):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    user_dto = FullUserInfoSchema.model_validate(user, from_attributes=True)
    set_token_cookies(user=user_dto, response=response, remember_me=payload.remember_me)
    return user_dto


@app.post("/logout")
async def logout(response: Response):
    delete_token_cookies(response)
    return {"message": "Logged out"}


@app.post("/refresh")
async def refresh(
    response: Response,
    current_user: RefreshUserDependency,
):
    set_token_cookies(user=current_user, response=response, remember_me=True)
    return {"message": "Refreshed"}


@app.post("/profile", response_model=UserProfileDBSchema)
async def create_profile(
    payload: CreateUserProfileSchema,
    session: AsyncSessionDependency,
    current_user: AccessUserDependency,
):
    if current_user.profile:
        raise HTTPException(status_code=409, detail="User already created an profile")
    new_profile = await create_user_profile(
        session=session, user_id=current_user.id, profile_info=payload
    )
    new_profile_dto = UserProfileDBSchema.model_validate(
        new_profile, from_attributes=True
    )
    return new_profile_dto


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
