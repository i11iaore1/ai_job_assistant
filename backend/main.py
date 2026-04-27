from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from api import router
from exceptions.base import BaseAppException
from exceptions.jwt_service import TokenReuse
from services.jwt_service import delete_token_cookies

app = FastAPI()

app.include_router(router)

add_pagination(app)

app.exception_handler(BaseAppException)


@app.exception_handler(BaseAppException)
async def base_exception_handler(request: Request, exc: BaseAppException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
    if isinstance(exc, TokenReuse):
        delete_token_cookies(response)

    return response
