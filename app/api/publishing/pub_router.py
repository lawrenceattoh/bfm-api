from fastapi import APIRouter

from .v1.publishers import router as router_publishers
from .v1.works import router as router_works
from .v1.writers import router as router_writers

router = APIRouter(tags=["publishing"])
router.include_router(router_works, tags=["works"])
router.include_router(router_writers, tags=["writers"])
router.include_router(router_publishers, tags=["publishers"])