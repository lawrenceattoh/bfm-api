
from fastapi import APIRouter

from app.schemas import common

router = APIRouter(prefix="/v1/copyright", tags=["copyright"])


#
# @router.get('/', response_model=common.MultiCopyrightResponse):
# async def get_copyrights():
#
