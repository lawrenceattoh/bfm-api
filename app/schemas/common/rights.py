import datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.schemas.utils import convert_date


class Licensee(BaseModel):
    name: str


class BaseRight(BaseModel):
    deal_id: str
    perf_share: Optional[float]
    right_type: str
    is_controlled: bool
    territories: Optional[List[str]]
    mechanical_share: Optional[float] = None
    third_party_admin: str | None = None
    reversion_date: datetime.date | None = None

    @field_validator('reversion_date', mode='before')
    @classmethod
    def convert_neo4j_date(cls, value):
        return convert_date(value)


class RightIdOptional(BaseModel):
    id: str | None = None


class RightId(BaseModel):
    id: str


class Right(BaseRight, RightId):
    pass


class CrudRight(BaseRight, RightIdOptional):
    pass


class AttachedRights(BaseModel):
    rights: List[Right]


class CrudRights(BaseModel):
    rights: List[CrudRight]
