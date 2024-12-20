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


class Writer(BaseModel):
    writer_id: str
    writer_name: str
    ipi: str


class WorkId(BaseModel):
    id: str


class Work(BaseNode, BaseWork, WorkId):
    writers: Optional[List[Writer]] = None


class CreateWork(BaseWork):
    writers: Optional[List[Writer]] = None


class WorkResponse(Work):
    class Config:
        crm_mode = True


class UpdateWork(BaseWork):
    writers: Optional[List[Writer]] = None


class MultiWorkResponse(BaseModel):
    works: List[Work]
    rowCount: int
    limit: int
    offset: int
    order: str
