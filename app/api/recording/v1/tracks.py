from fastapi import APIRouter

from app.api.utils import PaginationParams
from app.models.recordings import ModelTracks
from app.schemas.recording.track import MultiTrackResponse

router = APIRouter(prefix="/v1/tracks", tags=["Tracks"])


@router.get('/', response_model=MultiTrackResponse)
async def get_all_tracks(pagination_params: PaginationParams):
    t, c = ModelTracks.read_all(pagination_params=pagination_params)
    return MultiTrackResponse(tracks=t, rowCount=c, **pagination_params)
