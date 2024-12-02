from http.client import HTTPException
from typing import Optional, Annotated

from fastapi import APIRouter, Query, Depends

from app.api.utils import PaginationParams, get_user
from app.models.common import ModelBusinessEntity
from app.schemas import common
from app.schemas.utils import DeleteResponse

router = APIRouter(prefix='/v1/business-entities', tags=['business-entities'])


async def business_entity_search_params(
        _id: Optional[str] = Query(None, description="Group ID", alias="id"),
        name: Optional[str] = Query(None, description="Group name"),
        deal_name: Optional[str] = Query(None, description="Related Deal Name")):
    return {
        "id": _id,
        "name": name,
        "deal_name": deal_name
    }


BusinessEntitySearchParams = Annotated[dict, Depends(business_entity_search_params)]


@router.get('/', response_model=common.MultiBusinessEntityResponse)
async def get_business_entities(search_params: BusinessEntitySearchParams, pagination_params: PaginationParams):
    if entities := ModelBusinessEntity.read_all(search_params=search_params, pagination_params=pagination_params):
        e, row_count = entities
        return common.MultiBusinessEntityResponse(businessEntities=e, rowCount=row_count, **pagination_params)


@router.get('/{business_entity_id}', response_model=common.BusinessEntityResponse)
async def get_business_group(business_entity_id: str):
    if business_entity := ModelBusinessEntity.read_one(node_id=business_entity_id):
        return common.BusinessEntityResponse(**business_entity)


@router.post('/', response_model=common.BusinessEntityResponse)
async def create_business_group(business_entity: common.BaseBusinessEntity, rms_user: str = Depends(get_user)):
    business_entity = ModelBusinessEntity.create(params={**business_entity.model_dump(exclude_unset=True)},
                                                 rms_user=rms_user)
    return common.BusinessEntityResponse(**business_entity)


@router.patch('/{business_entity_id}', response_model=common.BusinessEntityResponse)
async def update_business_group(business_entity_id: str, node_params: common.BaseBusinessEntity,
                                rms_user: str = Depends(get_user)):
    group = ModelBusinessEntity.update(node_id=business_entity_id,
                                       params={'node_params': node_params.model_dump(exclude_unset=True)},
                                       rms_user=rms_user)
    return group


@router.delete('/{business_entity_id}', response_model=DeleteResponse)
async def delete_business_group(business_entity_id: str):
    try:
        group = ModelBusinessEntity.delete(business_entity_id)

        if group:
            return DeleteResponse(id=business_entity_id, entity_type='Business Group', message='Business Group Deleted')
        return DeleteResponse(id=business_entity_id, entity_type='Business Group',
                              message='Business Group does not exist or is deleted')
    except Exception as e:
        raise HTTPException(status_code=500)
