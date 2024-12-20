from typing import Optional, List, Dict

from fastapi import APIRouter, Query
from neomodel import db
from pydantic import BaseModel

from app.models._base import parse_neo_response

router = APIRouter(prefix='/v1/search')

cypher_search = '''
CALL db.index.fulltext.queryNodes('nameFulltextIndex', $searchTerm) YIELD node, score
RETURN node.id as nodeId, labels(node)[0] as nodeLabel, node.name as name
ORDER BY score DESC
limit 5
'''


class Results(BaseModel):
    items: Optional[List[Dict]]


@router.get('/')
async def search(q: str = Query(...)):
    r, s = db.cypher_query(cypher_search, {'searchTerm': q})
    return Results(items=parse_neo_response(r, s, True))
