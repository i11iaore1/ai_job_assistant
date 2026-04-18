from exceptions.base import BaseAppException


class TokenReuse(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Refresh token reuse detected. All sessions revoked",
            status_code=403,
        )
