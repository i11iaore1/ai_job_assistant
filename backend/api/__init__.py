from fastapi import APIRouter

from .reviews import router as review_router
from .users import router as user_router

router = APIRouter()

router.include_router(user_router, tags=["Users"])
router.include_router(review_router, tags=["Reviews"])
