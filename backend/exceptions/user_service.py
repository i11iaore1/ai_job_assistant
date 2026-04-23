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


class UserNotFound(BaseAppException):
    def __init__(self):
        super().__init__(
            message="User not found",
            status_code=404,
        )


class NoProfile(BaseAppException):
    def __init__(self):
        super().__init__(
            message="User doesn't have a profile",
            status_code=404,
        )


class NotResumeOwner(BaseAppException):
    def __init__(self):
        super().__init__(
            message="User does not have permission for the resume",
            status_code=403,
        )


class NotAdmin(BaseAppException):
    def __init__(self):
        super().__init__(
            message="User doesn't have enough privileges",
            status_code=403,
        )
