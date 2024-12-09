import datetime
from http.client import HTTPException
from typing import Optional, Annotated, List

import neo4j
from fastapi import APIRouter, Query, Depends
from neomodel import db
from pydantic import BaseModel, field_validator

from app.api.utils import get_user
from app.models import _base
from app.models.query_managers.misc.notes import get_notes_query, create_note_query

router = APIRouter(prefix="/v1/notes", tags=["notes"])


class Note(BaseModel):
    note: str
    created_by: str
    created_at: datetime.datetime

    @field_validator('created_at', mode='before')
    @classmethod
    def convert_neo4j_datetime_(cls, value):
        if isinstance(value, (neo4j.time.DateTime,)):
            return datetime.datetime(value.year, value.month, value.day, value.hour, value.minute, value.second)
        return value


class Notes(BaseModel):
    notes: List[Note]


class NoteCreate(BaseModel):
    note: str
    node_label: str
    entity_id: str


async def note_search_params(
        entityId: Optional[str] = Query(None),
        nodeLabel: Optional[str] = Query(None)

):
    return {
        "entity_id": entityId,
        "node_label": nodeLabel
    }


NoteSearchParams = Annotated[dict, Depends(note_search_params)]


@router.get("/", response_model=Notes)
async def get_notes(params: NoteSearchParams):
    print()
    print(get_notes_query())
    print(params)
    result, schema = db.cypher_query(get_notes_query(), params=params)
    print(result)
    return Notes(notes=_base.parse_neo_response(result, schema, is_many=True))


@router.post("/", response_model=Note)
async def create_note(note: NoteCreate, rms_user: str = Depends(get_user)):
    q = create_note_query()
    try:
        result, schema = db.cypher_query(q, params={**note.model_dump(exclude_unset=True), 'rms_user': rms_user})
        return _base.parse_neo_response(result, schema)
    except Exception as e:
        print(e)
        raise HTTPException()
