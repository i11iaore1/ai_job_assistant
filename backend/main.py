import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import reviews, users
from exceptions.base import BaseAppException
from exceptions.jwt_service import TokenReuse
from services.jwt_service import delete_token_cookies

app = FastAPI()


app.include_router(users.router, tags=["Users"])
app.include_router(reviews.router, tags=["Reviews"])


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


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
