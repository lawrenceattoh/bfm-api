from typing import List, Optional

from pydantic import BaseModel, model_validator

from app.schemas.base_node import BaseNode


class BasePublisher(BaseModel):
    name: Optional[str] = None
    ipi: Optional[str] = None


class CreatePublisher(BasePublisher):
    @model_validator(mode='before')
    def validate_for_create(cls, values):
        if any(value is None for value in values.values()):
            raise ValueError("All fields are required for the creation process")
        return values


class PublisherId(BaseModel):
    id: str


class Publisher(BaseNode, BasePublisher, PublisherId):
    pass


class UpdatePublisher(BasePublisher):
    pass


class PublisherResponse(Publisher):
    pass


class MultiPublisherResponse(BaseModel):
    publishers: List[PublisherResponse]
    rowCount: int
    limit: int
    offset: int
