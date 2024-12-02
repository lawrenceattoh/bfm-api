from typing import Annotated, Optional, List

from fastapi import APIRouter, Query, Depends

from app.api.utils import PaginationParams, get_user
from app.models.common import ModelDeal
from app.schemas.common.deals import DealResponse, MultiDealResponse, CreateDeal

router = APIRouter(prefix='/v1/deals', tags=['deals'])


async def deal_search_params(
        _id: Optional[str] = Query(None, description="ID of the deal", alias="id"),
        name: Optional[str] = Query(None, description="Deal name"),
        rights_type: Optional[List[str]] = Query(None, description="Rights type associated with deal",
                                                 alias="rights-type"),
        writer_id: Optional[str] = Query(None, description="Writer ID")

):
    return {
        "id": _id,
        "name": name,
        "rights_type": rights_type,
        "writer_id": writer_id
    }


DealSearchParams = Annotated[dict, Depends(deal_search_params)]


@router.post('/', response_model=DealResponse)
async def create_deal(deal: CreateDeal, rms_user=Depends(get_user)):
    deal = ModelDeal.create(params=deal.model_dump(exclude_unset=True), rms_user=rms_user)
    # Save files in cloud storage
    # deal.deal_id
    # save files
    print(deal)
    return DealResponse(**deal)


@router.get('/', response_model=MultiDealResponse)
async def get_deals(search_params: DealSearchParams, pagination_params: PaginationParams):
    if deals := ModelDeal.read_all(search_params=search_params, pagination_params=pagination_params):
        d, row_count = deals
        return MultiDealResponse(deals=d, rowCount=row_count, **pagination_params)
    return {'deals': []}


@router.get('/{deal_id}', response_model=DealResponse)
async def get_deal(deal_id: str):
    deal = ModelDeal.read_one(node_id=deal_id)
    return DealResponse(**deal)


@router.patch('/{deal_id}', response_model=DealResponse)
async def update_deal(deal_id: str, deal: CreateDeal, rms_user=Depends(get_user)):
    deal = ModelDeal.update(node_id=deal_id, params={'node_params': deal.model_dump(exclude_unset=True)},
                            rms_user=rms_user)
    return DealResponse(**deal)
