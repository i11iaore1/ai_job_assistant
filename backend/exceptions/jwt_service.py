from exceptions.base import BaseAppException


class TokenExpired(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Token expired",
            status_code=401,
        )


class TokenInvalid(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Token is invalid",
            status_code=401,
        )


class NotAuthenticated(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Not authenticated",
            status_code=401,
        )


class TokenTypeMismatch(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Token type mismatch",
            status_code=401,
        )


class TokenReuse(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Refresh token reuse detected. All sessions revoked",
            status_code=403,
        )
