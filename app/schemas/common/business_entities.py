from typing import List

from pydantic import BaseModel

from app.schemas.base_node import BaseNode
from app.schemas.utils import PaginatedResponse


class BaseBusinessEntity(BaseModel):
    name: str


class BusinessEntityId(BaseModel):
    id: str


class BusinessEntityResponse(BaseNode, BaseBusinessEntity, BusinessEntityId):
    pass


class BusinessEntities(BaseModel):
    businessEntities: List[BusinessEntityResponse]


class MultiBusinessEntityResponse(PaginatedResponse, BusinessEntities):
    pass
