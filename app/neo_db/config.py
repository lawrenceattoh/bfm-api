import logging
import os

from neomodel import config

logger = logging.getLogger(__name__)
build_env = os.environ.get("ENVIRONMENT", "dev")


def set_db_url():
    if build_env == "dev":
        print("Development environment selected")
        config.DATABASE_URL = "bolt://neo4j:mysecretpassword@localhost:7687"
        print(config.DATABASE_URL)
    elif build_env == "prod":
        print("Production environment selected")
        user = os.environ.get("NEO4J_USER")
        password = os.environ.get("NEO4J_PASS")
        uri = os.environ.get("NEO4J_URI")
        config.DATABASE_URL = "bolt://{}:{}@{}".format(user, password, uri)
        print(config.DATABASE_URL)
    else:
        print(f"Unknown environment {build_env}. Raising exception")
