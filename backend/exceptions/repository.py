from exceptions.base import BaseAppException


class RepositoryValidationError(BaseAppException):
    def __init__(self, fields: set[str]):
        super().__init__(
            message=f"Forbidden update fields: {sorted(fields)}",
            status_code=400,
        )
