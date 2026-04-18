import uvicorn
from fastapi import FastAPI

from api import reviews, users

app = FastAPI()

app.include_router(users.router, tags=["Users"])
app.include_router(reviews.router, tags=["Reviews"])


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
