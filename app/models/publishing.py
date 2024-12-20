from app.models._base import AbstractNode
from app.models.query_managers.publishing import WriterQueryManager, WorkQueryManager, PublisherQueryManager

writer = type('Writer', (AbstractNode,),
              {'node_alias': 'w', 'return_params': ['id', 'name', 'alias', 'ipi'], 'order_key': 'name'})
work = type('Work', (AbstractNode,), {'node_alias': 'wrk', 'return_params': ['iswc', 'name'], 'order_key': 'name'})
publisher = type('Publisher', (AbstractNode,),
                 {'node_alias': 'p', 'return_params': ['id', 'name', 'ipi'], 'order_key': 'name'})

ModelWriter = writer(WriterQueryManager(alias='wri', _id='WRI', label='Writer'))
ModelWork = work(WorkQueryManager(alias='wrk', _id='WRK', label='Work'))
ModelPublisher = publisher(PublisherQueryManager(alias='p', _id='PUB', label='Publisher'))
