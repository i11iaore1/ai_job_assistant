from exceptions.base import BaseAppException


class NoSuchResume(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Resume was not found",
            status_code=404,
        )


class NoSuchBucket(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Storage is not initialized",
            status_code=500,
        )


class StorageUnavailable(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Storage is currently unavailable. please try again later",
            status_code=503,
        )


class StorageError(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Something went wrong during storage operation",
            status_code=500,
        )
