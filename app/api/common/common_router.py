from fastapi import APIRouter

from app.api.common.v1.attachments import router as attachments_router
from app.api.common.v1.business_entity import router as entity_router
from app.api.common.v1.deal import router as deal_router
from app.api.common.v1.file_import import router as import_router
from app.api.common.v1.notes import router as notes_router
from app.api.common.v1.rights import router as rights_router
from app.api.common.v1.search import router as search_router
from app.api.common.v1.users import router as users_router

router = APIRouter(tags=["common"])
router.include_router(deal_router)
router.include_router(entity_router)
router.include_router(import_router)
router.include_router(users_router)
router.include_router(notes_router)
router.include_router(attachments_router)
router.include_router(rights_router)
router.include_router(search_router)
