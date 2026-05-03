from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from api import router
from config import app_config
from exceptions.base import BaseAppException
from exceptions.jwt_service import TokenReuse
from services.jwt_service import delete_token_cookies

app = FastAPI(
    title="AI Job Assistant",
    description="REST API for reviewing vacancy descriptions based on given resume and context",
    version=app_config.app_version,
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix=f"/api/{app_config.app_version}")

add_pagination(app)


@app.exception_handler(BaseAppException)
async def base_exception_handler(request: Request, exc: BaseAppException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
    if isinstance(exc, TokenReuse):
        delete_token_cookies(response)

    return response
