import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from ..base_node import BaseNode


class Scope(Enum):
    WORLDWIDE = "worldwide"
    CONTINENT = "continent"
    REGION = "region"
    COUNTRY = "country"


class RightType(Enum):
    WRITER_SHARE = "writer_share"
    PUBLISHER_SHARE = "publisher_share"


class BaseWork(BaseModel):
    name: str
    iswc: Optional[str] = None
    reversion_date: Optional[datetime.date] = None
    territories: Optional[List[str]] = None


class RightsHolder(BaseModel):
    deal_id: str
    id: str
    name: str
    share: float | None
    ipi: str
    internal_ip_ref: int


# class RightsHolder(BaseModel):
#     id: str
#     share: float | None
#     # ipi: str
#     internal_ip_ref: int
#

class PublisherInfo(RightsHolder):
    mech_share: Optional[float] = None
    is_controlled: Optional[bool] = None


class WriterInfo(RightsHolder):
    pass


class WorkId(BaseModel):
    id: str


class Work(BaseNode, BaseWork, WorkId):
    publishers: Optional[List[PublisherInfo]] = None
    writers: Optional[List[WriterInfo]] = None


class RightsHolderLite(BaseModel):
    deal_id: str
    id: str
    share: float


class PublisherLite(RightsHolderLite):
    mech_share: Optional[float] = None
    is_controlled: Optional[bool] = None


class WriterLite(RightsHolderLite):
    pass


class CreateWork(BaseWork):
    publishers: Optional[List[PublisherLite]] = None
    writers: Optional[List[WriterLite]] = None


class WorkResponse(Work):
    class Config:
        crm_mode = True


class MultiWorkResponse(BaseModel):
    works: List[Work]
    rowCount: int
    limit: int
    offset: int
    order: str



