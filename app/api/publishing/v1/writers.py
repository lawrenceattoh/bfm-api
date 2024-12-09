from typing import Annotated

from fastapi import APIRouter, Query, Depends

from app.api.utils import PaginationParams, get_user
from app.models.common import ModelDeal
from app.models.publishing import ModelWriter, ModelWork
from app.schemas import common
from app.schemas.publishing.work import MultiWorkResponse
from app.schemas.publishing.writer import MultiWriterResponse, WriterResponse, BaseWriter

router = APIRouter(prefix='/v1/writers', tags=['writers'])


async def writer_search_params(
        _id=Query(None, description="ID of the writer", alias="id", ),
        name=Query(None, description="Name of the writer - will partially match"),
        ipi=Query(None, description="Writers IPI number")

):
    return {
        "id": _id,
        "name": name,
        "ipi": ipi
    }


WriterSearchParams = Annotated[dict, Depends(writer_search_params)]


@router.get('/')
async def get_writers(search_params: WriterSearchParams, pagination_params: PaginationParams):
    writers, row_count = ModelWriter.read_all(search_params=search_params, pagination_params=pagination_params)
    print(writers)
    if writers:
        return MultiWriterResponse(writers=writers, rowCount=row_count,
                                   limit=min(int(pagination_params.get('limit')), row_count),
                                   offset=pagination_params.get('offset'), order=pagination_params.get('order'))
    return {'writers': []}


@router.get('/{writer_id}')
async def get_writer(writer_id: str):
    writer = ModelWriter.read_one(params={'id': writer_id})
    return WriterResponse(**writer)


@router.post('/')
async def create_writer(writer: BaseWriter, rms_user: str = Depends(get_user)):
    ModelWriter.create(params={**writer.model_dump(exclude_unset=True)}, rms_user=rms_user)
    pass


@router.get('/{writer_id}/deals')
async def get_writer_deals(writer_id: str, pagination_params: PaginationParams):
    if deals := ModelDeal.read_all(search_params={'writer_id': writer_id}, pagination_params=pagination_params):
        d, row_count = deals
        return common.MultiDealResponse(deals=d, rowCount=row_count, **pagination_params)


@router.get('/{writer_id}/works')
async def get_writer_works(writer_id: str, pagination_params: PaginationParams):
    if works := ModelWork.read_all(search_params={'writer_id': writer_id}, pagination_params=pagination_params):
        w, row_count = works
        return MultiWorkResponse(works=w, rowCount=row_count, **pagination_params)
