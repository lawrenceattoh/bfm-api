from typing import List, Optional

from pydantic import BaseModel, model_validator

from app.schemas.base_node import BaseNode


class BaseWriter(BaseModel):
    alias: Optional[str] = None
    name: Optional[str] = None
    ipi: Optional[str] = None


class CreateWriter(BaseWriter):
    @model_validator(mode='before')
    def validate_for_create(cls, values):
        if any(value is None for value in values.values()):
            raise ValueError("All fields are required for the creation process")
        return values


class WriterId(BaseModel):
    id: str


class Writer(BaseNode, BaseWriter, WriterId):
    pass


class UpdateWriter(BaseWriter):
    pass


class WriterResponse(Writer):
    pass


class MultiWriterResponse(BaseModel):
    writers: List[WriterResponse]
    rowCount: int
    limit: int
    offset: int
