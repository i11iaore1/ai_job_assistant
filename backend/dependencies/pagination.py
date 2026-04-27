from typing import Annotated

from fastapi import Depends, Query
from fastapi_pagination import Params


class CustomParams(Params):
    size: int = Query(10, ge=1, le=50)


PaginationParams = Annotated[CustomParams, Depends()]
