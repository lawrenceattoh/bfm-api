import os

from fastapi import FastAPI
from firebase_admin import initialize_app
from neomodel import UniqueProperty
from neomodel import db
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.common.common_router import router as common_router
from app.api.exceptions import DoesNotExist
from app.api.publishing.pub_router import router as publishing_router
from app.api.rbac.rbac_middleware import RBACMiddleware
from app.api.recording.rec_router import router as recording_router
from app.neo_db.config import set_db_url

app = FastAPI()
set_db_url()

fb = initialize_app(options={'projectId': 'bfm-sandbox'})

proc_generate_node_id = '''
use system
call apoc.custom.installProcedure(
    'addNodeId(node::NODE, prefix::STRING) :: (node::NODE)',
    'WITH $node AS node, $prefix AS prefix
     CALL apoc.do.when(
         node.id IS NULL,
         "CALL custom.generateId(apoc.node.labels(node)[0], prefix) YIELD entityId SET node.id = entityId RETURN node",
         "RETURN node",
         {node: node, prefix: prefix}
     ) YIELD value
     RETURN value.node AS node',
     'neo4j',
    'WRITE'
)'''

proc_generate_custom_id = '''
use system
CALL apoc.custom.installProcedure(
  'generateId(label :: STRING, prefix :: STRING) :: (entityId::STRING)',
  'MERGE (counter:Counter {name: $label + "Counter"})
   ON CREATE SET counter.value = 0
   SET counter.value = counter.value + 1
   WITH counter
   RETURN $prefix +"-" + apoc.text.lpad(toString(counter.value), 6, "0") as entityId',
   'neo4j',
    'WRITE'
);'''

create_bfm_publisher = '''
merge (p:Publisher {name: 'BELLA FIGURA MUSIC', ipi: '1133481777'})
with p
    call custom.addNodeId(p, 'PUB') yield node as _pub 
return p
'''

create_search_index = '''
CREATE FULLTEXT INDEX nameFulltextIndex if not exists
FOR (n:Artist|BusinessEntity|Work|Writer|Deal)
ON EACH [n.name];
'''


# CREATE FULLTEXT INDEX dealSearchIndex
# FOR (n:Deal)
# ON EACH [n.name,n.id]


# create index for (n:BusinessEntity) ON (n.id, n.name)


def init_procedures():
    print('running init procedures')
    db.cypher_query(proc_generate_node_id)
    db.cypher_query(proc_generate_custom_id)
    db.cypher_query(create_bfm_publisher)
    db.cypher_query(create_search_index)


@app.exception_handler(UniqueProperty)
async def unique_property_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Item already exists in the database"},
    )


@app.exception_handler(DoesNotExist)
async def does_not_exist_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Item does not exist"},
    )


# os.environ['ENVIRONMENT'] = 'prod'
if os.environ.get("ENVIRONMENT") == "prod":
    # app.dependency_overrides[check_user_firebase_auth] = check_user_firebase_auth
    app.add_middleware(RBACMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "localhost:3000",
        "https://rms.bellafiguramusic.com",
        "https://bfm-sandbox.web.app",
        "http://127.0.0.1:5000",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)
init_procedures()

app.include_router(publishing_router, prefix='/api')
app.include_router(common_router, prefix="/api")
app.include_router(recording_router, prefix="/api")
