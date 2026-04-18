from exceptions.base import BaseAppException


class EmailConflict(BaseAppException):
    def __init__(self):
        super().__init__(
            message="User with this email already exists",
            status_code=409,
        )


class WrongCredentials(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Wrong email or password",
            status_code=401,
        )


class ProfileConflict(BaseAppException):
    def __init__(self):
        super().__init__(
            message="User already has a profile",
            status_code=409,
        )
