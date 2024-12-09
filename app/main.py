import os

from fastapi import FastAPI
from firebase_admin import initialize_app, credentials
from neomodel import UniqueProperty
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.common.common_router import router as common_router
from app.api.exceptions import DoesNotExist
from app.api.publishing.pub_router import router as publishing_router
from app.api.rbac.rbac_middleware import RBACMiddleware

app = FastAPI()

sa_file = '/Users/tristancrudge/Downloads/rms-dev-e3394-firebase-adminsdk-7zstb-3120678b5e.json'  # Local only

cred = credentials.Certificate(sa_file)
fb = initialize_app(cred)

from neomodel import db, config

config.DATABASE_URL = config.DATABASE_URL = "bolt://neo4j:password@localhost:7687"

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


# CREATE FULLTEXT INDEX dealSearchIndex
# FOR (n:Deal)
# ON EACH [n.name,n.id]


# create index for (n:BusinessEntity) ON (n.id, n.name)




def init_procedures():
    print('running init procedures')
    db.cypher_query(proc_generate_node_id)
    db.cypher_query(proc_generate_custom_id)
    db.cypher_query(create_bfm_publisher)


# fb = initialize_app()


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


# os.environ["ENVIRONMENT"] = "prod"
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
        "https://rms-dev-e3394.web.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)
init_procedures()

app.include_router(publishing_router, prefix='/api')
app.include_router(common_router, prefix="/api")
