from typing import List

from pydantic import BaseModel

from ..base_node import BaseNode


class BaseArtist(BaseModel):
    name: str


class ArtistId(BaseModel):
    id: str


class Artist(BaseNode, BaseArtist, ArtistId):
    pass


class MultiArtistsResponse(BaseModel):
    artists: List[Artist]
    rowCount: int
    limit: int
    offset: int
    order: str
