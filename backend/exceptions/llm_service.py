from exceptions.base import BaseAppException


class LLMServiceException(BaseAppException):
    def __init__(
        self,
        message: str = "Something went wrong during LLM request processing",
        status_code: int = 500,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
        )
