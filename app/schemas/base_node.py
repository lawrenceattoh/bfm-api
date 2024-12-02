import datetime
from typing import Optional

import neo4j
from pydantic import BaseModel, field_validator

from app.schemas.utils import convert_datetime


class BaseNode(BaseModel):
    created_by: str
    created_at: datetime.datetime
    updated_by: str
    updated_at: datetime.datetime
    is_deleted: bool
    create_method: Optional[str] = None
    status: Optional[str] = None

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def convert_neo4j_datetime(cls, value):
        return convert_datetime(value)
