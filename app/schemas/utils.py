import datetime

import neo4j
from pydantic import BaseModel


def convert_date(value):
    if isinstance(value, (neo4j.time.Date,)):
        return datetime.date(value.year, value.month, value.day)
    elif isinstance(value, str):
        return datetime.datetime.strptime(value, '%Y-%m-%d').date()
    return value


def convert_datetime(value):
    if isinstance(value, (neo4j.time.DateTime,)):
        return datetime.datetime(value.year, value.month, value.day, value.hour, value.minute, value.second)
    return value


class PaginatedResponse(BaseModel):
    rowCount: int
    offset: int
    limit: int
    order: str


class DeleteResponse(BaseModel):
    id: str
    entity_type: str
    deleted: bool = True
    message: str
