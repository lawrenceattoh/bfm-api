from typing import Annotated

from fastapi import APIRouter, Query, Depends, HTTPException

from app.api.utils import PaginationParams, get_user
from app.models.recordings import ModelArtist
from app.schemas.recording.artist import BaseArtist, MultiArtistsResponse, Artist
from app.schemas.utils import DeleteResponse

router = APIRouter(prefix='/v1/artists', tags=['artists'])


def artist_search_params(
        _id=Query(None, alias='id'),
        name=Query(None),
        trackName=Query(None)):
    return {
        'id': _id,
        "name": name,
        "track_name": trackName
    }


ArtistSearchParams = Annotated[dict, Depends(artist_search_params)]


@router.get('/', response_model=MultiArtistsResponse)
async def get_artists(search_params: ArtistSearchParams, pagination_params: PaginationParams):
    artists, row_count = ModelArtist.read_all(search_params=search_params, pagination_params=pagination_params)
    return MultiArtistsResponse(artists=artists, rowCount=row_count, **pagination_params)


@router.get('/{artist_id}', response_model=Artist)
async def get_artist(artist_id: str):
    a = ModelArtist.read_one(node_id=artist_id)
    return Artist(**a)


@router.post('/', response_model=Artist)
async def create_artist(artist: BaseArtist, rms_user=Depends(get_user)):
    a = ModelArtist.create(params=artist.model_dump(exclude_unset=True), rms_user=rms_user)
    return Artist(**a)


@router.patch('/{artist_id}', response_model=Artist)
async def update_artist(artist_id: str, artist: BaseArtist, rms_user=Depends(get_user)):
    print(artist)
    a = ModelArtist.update(artist_id, params={'node_params': artist.model_dump(exclude_unset=True)}, rms_user=rms_user)
    return Artist(**a)


@router.delete('/{artist_id}', response_model=DeleteResponse)
async def delete_artist(artist_id: str):
    try:
        a = ModelArtist.delete(artist_id)
        print(a)
        if a:
            return DeleteResponse(id=artist_id, entity_type='Artist', message='Artist deleted')
        return DeleteResponse(id=artist_id, entity_type='Artist', message='Artist does not exist or has been deleted')
    except Exception as e:
        raise HTTPException(status_code=500)
