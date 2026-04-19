from exceptions.base import BaseAppException


class LLMRequestProcessedIncorrectly(BaseAppException):
    def __init__(self):
        super().__init__(
            message="LLM didn't process request correctly",
            status_code=502,
        )
