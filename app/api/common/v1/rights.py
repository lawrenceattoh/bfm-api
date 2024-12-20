from fastapi import APIRouter, Depends

from app.api.utils import get_user
from app.models.query_managers.common.rights import RightsNode
from app.schemas.common.rights import AttachedRights, CrudRights

router = APIRouter(prefix="/v1/rights", tags=["rights"])


@router.get("/{node_id}", response_model=AttachedRights)
async def get_rights(node_id: str):
    return RightsNode.get_attached_rights(node_id)


@router.patch("/{node_id}", response_model=AttachedRights)
async def update_rights(node_id: str, data: CrudRights, rms_user=Depends(get_user)):
    rights = [r.model_dump() for r in data.rights]
    print(rights)
    return RightsNode.update_rights(node_id, rights=rights,
                                    rms_user=rms_user)
