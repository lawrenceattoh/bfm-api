from app.models._query_manager import AbstractQueryManager


class BusinessEntityQueryManager(AbstractQueryManager):

    def __init__(self):
        super().__init__(alias='be', label='BusinessEntity', _id='BFM')

    _create = 'merge (be:BusinessEntity{name: $params.name}) '

    _search = ('with be '
               'WHERE (tolower(be.name) CONTAINS tolower($params.name) OR $params.name IS NULL) '
               'optional match (be)-[:PARENT_CO]-(existingDeal:Deal) '
               'where '
               '(tolower(existingDeal.name) contains $params.deal_name or $params.deal_name is null)'
               'with be, existingDeal '
               'where $params.rights_type is null or (existingDeal is not null and existingDeal.rights_type = $params.rights_type)')

    def _return(self):
        return ('return distinct be.name as name, '
                'be.id as id, ') + self.add_base_params('be')
