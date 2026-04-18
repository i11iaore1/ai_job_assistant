import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import reviews, users
from exceptions.base import BaseAppException

app = FastAPI()


app.include_router(users.router, tags=["Users"])
app.include_router(reviews.router, tags=["Reviews"])


app.exception_handler(BaseAppException)


@app.exception_handler(BaseAppException)
async def base_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
