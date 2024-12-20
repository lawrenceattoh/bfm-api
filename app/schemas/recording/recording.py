from typing import List

from pydantic import BaseModel

from ..base_node import BaseNode


class BaseRecording(BaseModel):
    isrc: str | None = None
    version: str | None = None
    track_name: str
    # contributors


class RecordingId(BaseModel):
    id: str


class Recording(BaseNode, BaseRecording, RecordingId):
    pass


class MultiRecordingResponse(BaseModel):
    recordings: List[Recording]
    rowCount: int
    limit: int
    offset: int
    order: str
