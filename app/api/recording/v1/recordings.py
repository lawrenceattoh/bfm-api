from fastapi import APIRouter, Query

from app.api.utils import PaginationParams
from app.models.recordings import ModelRecordings
from app.schemas.recording.recording import MultiRecordingResponse, Recording

router = APIRouter(prefix="/v1/recordings", tags=["recordings"])


def recordings_search_params(
        name: str = Query()

):
    return {"name": ""}


@router.get("/", response_model=MultiRecordingResponse)
async def get_recordings(pagination_params: PaginationParams):
    r, c = ModelRecordings.read_all(pagination_params=pagination_params)
    return MultiRecordingResponse(recordings=r, rowCount=c, **pagination_params)


@router.get("/{recording_id}", response_model=Recording)
async def get_recordings(recording_id: str):
    r = ModelRecordings.read_one(node_id=recording_id)
    return Recording(**r)
