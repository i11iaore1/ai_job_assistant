from exceptions.base import BaseAppException


class FileTooBig(BaseAppException):
    def __init__(self):
        super().__init__(
            message="File exceeds maximum size",
            status_code=413,
        )


class InvalidFileExtension(BaseAppException):
    def __init__(self):
        super().__init__(
            message="File extension is invalid",
            status_code=400,
        )
