from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str = "success"
    message: str | None = None
