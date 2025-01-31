import logging
from abc import ABC, abstractmethod

import jinja2
from neomodel import db

from app.models._query_manager import AbstractQueryManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_add_pagination = '''
{{ q }}
order by {{ order_key }} {{ order }}
skip {{ offset }}
limit {{ limit }}
'''


def parse_neo_response(result, schema, is_many=False):
    data = [dict(zip(schema, r)) for r in result]
    if is_many:
        return data if data else []
    return data[0] if data else {}


def validate_kwargs(input_keys, expected_keys):
    return False if set(input_keys) - set(expected_keys) else True


class AbstractNode(ABC):

    def __init__(self, query_manager: AbstractQueryManager):
        self.query_manager = query_manager

    @property
    @abstractmethod
    def order_key(self):
        pass

    @property
    @abstractmethod
    def return_params(self):
        pass

    def _log_query(self, action, query, params, response=None, row_count=None):
        logger.info(f"Action: {action}")
        logger.info(f"Query: {query}")
        logger.info(f"Params: {params}")
        if response is not None:
            logger.info(f"Records Returned: {len(response)}")
        if row_count is not None:
            logger.info(f"Total Row Count: {row_count}")

    def create(self, *, neodb=db, params: dict = None, rms_user: str = None):
        q = self.query_manager.create()
        print(q)
        result, schema = neodb.cypher_query(q, {'params': params, 'rms_user': rms_user})
        response = parse_neo_response(result, schema)
        return response

    def read_one(self, node_id, *, neodb=db, params: dict = None):
        q = self.query_manager.read_one()
        result, schema = neodb.cypher_query(q, {'id': node_id, 'params': params})
        response = parse_neo_response(result, schema)
        return response

    def read_all(self, *, neodb=db, search_params: dict = {}, pagination_params: dict = {}):
        read_all_count = self.query_manager.read_all_count()
        row_count_result, _ = neodb.cypher_query(read_all_count, {'params': search_params})
        row_count = row_count_result[0][0]

        q = self.query_manager.read_all()
        print(q)
        order_key = f'{self.query_manager.alias}.{self.order_key}' if '.' not in self.order_key else self.order_key
        pq = jinja2.Template(_add_pagination).render(
            q=q, order_key=f'{order_key}', **pagination_params
        )
        result, schema = neodb.cypher_query(pq, {'params': search_params})
        response = parse_neo_response(result, schema, is_many=True)

        return response if response else [], row_count

    def update(self, node_id, *, neodb=db, params: dict = None, rms_user: str = None):
        q = self.query_manager.update()
        result, schema = neodb.cypher_query(q, {'id': node_id, 'params': params, 'rms_user': rms_user})
        response = parse_neo_response(result, schema)
        return response

    def delete(self, node_id, *, neodb=db, rms_user: str = None):
        q = self.query_manager.delete()
        print(q)
        result, schema = neodb.cypher_query(q, {'id': node_id, 'rms_user': rms_user})
        response = parse_neo_response(result, schema)
        return response
