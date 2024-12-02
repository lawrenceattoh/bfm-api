from typing import Annotated

from fastapi import APIRouter, Query, Depends

from app.api.utils import PaginationParams
from app.models.publishing import ModelWriter, ModelPublisher
from app.schemas.publishing.publisher import MultiPublisherResponse, PublisherResponse

router = APIRouter(prefix='/v1/publishers', tags=['writers'])


async def publisher_search_params(
        _id=Query(None, description="ID of the publisher", alias="id"),
        name=Query(None, description="Name of the publisher- will partially match"),
        ipi=Query(None, description="Writers IPI publisher")

):
    return {
        "id": _id,
        "name": name,
        "ipi": ipi
    }


PublisherSearchParams = Annotated[dict, Depends(publisher_search_params)]


@router.get('/')
async def get_publisher(search_params: PublisherSearchParams, pagination_params: PaginationParams):
    if publishers := ModelPublisher.read_all(search_params=search_params, pagination_params=pagination_params):
        p, row_count = publishers
        return MultiPublisherResponse(publishers=p, rowCount=row_count, **pagination_params)
    return {'publishers': []}


@router.get('/{pub_id}')
async def get_publisher(pub_id: str):
    writer = ModelWriter.read_one(params={'id': pub_id})
    return PublisherResponse(**writer)

# @router.post('/')
# async def create_publisher(writer: BaseWriter, rms_user: str = Depends(get_user)):
#     ModelWriter.create(params={**writer.model_dump(exclude_unset=True)}, rms_user=rms_user)
