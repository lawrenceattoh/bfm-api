from http.client import HTTPException
from typing import Optional, Annotated

from fastapi import APIRouter, Query, Depends

from app.api.utils import PaginationParams, get_user
from app.models.recordings import ModelTracks
from app.schemas.recording.track import MultiTrackResponse, Track, BaseTrack
from app.schemas.utils import DeleteResponse

router = APIRouter(prefix="/v1/tracks", tags=["Tracks"])


async def track_search_params(
        _id: Optional[str] = Query(None, alias="id", description="Track ID"),
        track_name: Optional[str] = Query(None, alias='trackName'),
        artist_name: Optional[str] = Query(None, alias="artistName"),
        artist_id: Optional[str] = Query(None, alias="artistId")
        # contributor_name: Optional[str] = Query(None, alias="contributorName")

):
    return {
        "id": _id,
        "track_name": track_name,
        "artist_name": artist_name,
        "artist_id": artist_id

        # "contributor_name": contributor_name
    }


TrackSearchParams = Annotated[dict, Depends(track_search_params)]


@router.get('/', response_model=MultiTrackResponse)
async def get_all_tracks(track_search_params: TrackSearchParams, pagination_params: PaginationParams):
    t, c = ModelTracks.read_all(search_params=track_search_params, pagination_params=pagination_params)
    print(track_search_params)
    return MultiTrackResponse(tracks=t, rowCount=c, **pagination_params)


@router.get('/{track_id}', response_model=Track)
async def get_track(track_id: str):
    print(track_id)
    t = ModelTracks.read_one(node_id=track_id)
    print(t, 'GET ONE')
    return Track(**t)


@router.post('/', response_model=Track)
async def create_track(track: BaseTrack, rms_user: str = Depends(get_user)):
    t = ModelTracks.create(params={**track.model_dump(exclude_unset=True)}, rms_user=rms_user)
    print(t)
    return Track(**t)


@router.patch('/{track_id}', response_model=Track)
async def update_track(track_id: str, track: BaseTrack, rms_user: str = Depends(get_user)):
    node_params = track.model_dump(exclude_unset=True)
    artist_id = node_params.pop('artist_id')
    print(node_params)
    print(artist_id)

    t = ModelTracks.update(track_id, params={'node_params': node_params, 'artist_id': artist_id}, rms_user=rms_user)
    return Track(**t)


@router.delete('/{track_id}', response_model=DeleteResponse)
async def delete_track(track_id: str):
    try:
        t = ModelTracks.delete(track_id)
        if t:
            return DeleteResponse(id=track_id, entity_type='Track', message='Work deleted')
        return DeleteResponse(id=track_id, entity_type='Track', message='Work does not exist or is already deleted')
    except Exception as e:
        raise HTTPException(status_code=500)
