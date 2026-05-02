from exceptions.base import BaseAppException


class ReviewNotFound(BaseAppException):
    def __init__(self):
        super().__init__(
            message="Review not found",
            status_code=404,
        )
