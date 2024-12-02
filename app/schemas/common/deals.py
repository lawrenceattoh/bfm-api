import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, field_validator

from app.schemas.base_node import BaseNode
from app.schemas.utils import convert_date, PaginatedResponse


class BaseDeal(BaseModel):
    name: str | None = None
    completed_date: Optional[datetime.date] = None

    @field_validator('completed_date', mode='before')
    @classmethod
    def validate_completed_date(cls, value):
        return convert_date(value)


class DealId(BaseModel):
    id: str


class PurchasedAssets(BaseModel):
    works: Optional[List[Any]] = None
    recordings: Optional[List[Any]] = None


class BusinessGroupId(BaseModel):
    business_group_id: str


class CreateDeal(BaseDeal, BusinessGroupId):
    pass


class Deal(BaseNode, BaseDeal, DealId):
    rights_types: List[str] = None
    # assets: PurchasedAssets


class DealResponse(Deal):
    pass


class Deals(BaseModel):
    deals: List[DealResponse]


class MultiDealResponse(PaginatedResponse, Deals):
    pass
