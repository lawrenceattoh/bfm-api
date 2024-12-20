from fastapi import APIRouter

from .v1.artists import router as router_artists
from .v1.recordings import router as router_recordings
from .v1.tracks import router as router_tracks

router = APIRouter(tags=["recording"])

router.include_router(router_artists)
router.include_router(router_recordings)
router.include_router(router_tracks)
