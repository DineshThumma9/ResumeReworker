from fastapi import APIRouter

from api.routes.auth import router as auth_router
from api.routes.resumes import router as resumes_router
from api.routes.setup import router as setup_router
from api.routes.share import router as share_router
from api.routes.templates import router as templates_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(resumes_router)
router.include_router(setup_router)
router.include_router(share_router)
router.include_router(templates_router)
