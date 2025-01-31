from typing import List, Optional

from pydantic import BaseModel

from ..base_node import BaseNode


# class Artist(BaseModel):
#     id: str
#     artist_name: str
#     artist_id: str
#
#
class BaseTrack(BaseModel):
    name: str
    artist_name: Optional[str] = None  # For searching only
    artist_id: str


class TrackId(BaseModel):
    id: str


class Track(BaseNode, BaseTrack, TrackId):
    pass


class MultiTrackResponse(BaseModel):
    tracks: List[Track]
    rowCount: int
    limit: int
    offset: int
    order: str
