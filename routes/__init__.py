"""Route package — aggregates all API routers."""

from fastapi import APIRouter

from routes.init import router as init_router
from routes.kabupaten import router as kabupaten_router
from routes.jadwal import router as jadwal_router

router = APIRouter()
router.include_router(init_router)
router.include_router(kabupaten_router)
router.include_router(jadwal_router)
