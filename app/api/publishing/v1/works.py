from typing import Annotated

from fastapi import APIRouter, Query, Depends, HTTPException

from app.api.utils import PaginationParams, get_user
from app.models.publishing import ModelWork
from app.schemas.publishing.work import MultiWorkResponse, WorkResponse, CreateWork, UpdateWork
from app.schemas.utils import DeleteResponse

router = APIRouter(prefix='/v1/works', tags=['works'])


async def work_search_params(
        _id=Query(None, description="ID of the writer", alias="id"),
        writer_name=Query(None, description="Name of the writer - will partially match", alias="writerName"),
        writer_id=Query(None, description="ID of the writer - will partially", alias="writerId"),
        name=Query(None, description="Name of the work"),
        status=Query(None, description="Writer node status"),
        iswc=Query(None, description="Writers IPI number ")

):
    return {
        "id": _id,
        "name": name,
        "writer_name": writer_name,
        "writer_id": writer_id,
        "status": status,
        "iswc": iswc,
    }


WorkSearchParams = Annotated[dict, Depends(work_search_params)]


@router.get('/')  # response_model=)
async def get_works(work_search_params: WorkSearchParams, pagination_params: PaginationParams):
    if works := ModelWork.read_all(search_params=work_search_params, pagination_params=pagination_params):
        w, row_count = works
        print(w)
        return MultiWorkResponse(works=w, rowCount=row_count, **pagination_params)
    return {'writers': []}


@router.get('/{work_id}')
async def get_work(work_id: str):
    work = ModelWork.read_one(node_id=work_id)
    return WorkResponse(**work)


@router.post('/')
async def create_work(work: CreateWork, rms_user=Depends(get_user)):
    work = ModelWork.create(params={**work.model_dump(exclude_unset=True)}, rms_user=rms_user)
    return work


@router.patch('/{work_id}')
async def update_work(work_id: str, work: UpdateWork, rms_user=Depends(get_user)):
    writers = work.writers if work.writers else []
    del work.writers
    writers = [w.model_dump(exclude_unset=True) for w in writers]
    work = ModelWork.update(node_id=work_id,
                            params={'node_params': work.model_dump(exclude_unset=True),
                                    'writers': writers},
                            rms_user=rms_user)
    return work


@router.delete('/{work_id}', response_model=DeleteResponse)
async def delete_work(work_id: str):
    try:
        w = ModelWork.delete(work_id)
        if w:
            return DeleteResponse(id=work_id, entity_type='Work', message='Work deleted')
        return DeleteResponse(id=work_id, entity_type='Work', message='Work does not exist or is already deleted')
    except Exception as e:
        raise HTTPException(status_code=500)
