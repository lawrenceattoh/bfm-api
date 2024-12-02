from app.models._base import AbstractNode
from app.models.query_managers.common import BusinessEntityQueryManager, DealQueryManager


class Deal(AbstractNode):
    return_params = ['name', 'completed_date']
    order_key = 'name'


class BusinessEntity(AbstractNode):
    return_params = ['name']
    order_key = 'name'


class Copyright(AbstractNode):
    return_params = ['type']
    order_key = 'name'


ModelDeal = Deal(DealQueryManager())
ModelBusinessEntity= BusinessEntity(BusinessEntityQueryManager())
