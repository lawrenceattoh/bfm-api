from app.models._query_manager import AbstractQueryManager


class DealQueryManager(AbstractQueryManager):

    def __init__(self):
        super().__init__(alias='d', _id='DEA', label='Deal')

    @property
    def _create(self) -> str:
        return '''
        merge (d:Deal {name: $params.name}) 
            set d.completed_date = $params.completed_date
        '''

    @property
    def _search(self) -> str:
        return '''
        with d 
        where 
            (tolower(d.name) contains tolower($params.name) or $params.name is null)
        optional match (d)-[:DEAL_TYPE]-(c:Copyright) 
        where 
            (c.type in $params.rights_type or $params.rights_type is null)
        optional match (d)-[:PURCHASED_ASSET]-(wrk:Work)-[:ROYALTY_SHARE]-(:IpChain)-[:WRITER_SHARE]-(wri:Writer)
        where 
            (wri.id = $params.writer_id or $params.writer_id is null)
        with d, c
        '''

    @property
    def _with_relations(self) -> str:
        return '''
        with * 
            call (*) {
                with d, $params.business_group_id as business_group_id
                where business_group_id is not null 
                optional match (d)-[existingParentCo:PARENT_CO]-(existingBG:BusinessGroup)
                with d, existingBG, business_group_id, existingParentCo
                match (newBG:BusinessGroup {id: business_group_id})
                foreach (_ in case when business_group_id = existingBG.id then [] else [1] end |
                delete (existingParentCo)
                merge (d)<-[:PARENT_CO]-(newBG)
                )
            }
        '''

    def _return(self) -> str:
        return '''
        with d 
        optional match (d)-[:DEAL_TYPE]-(c:Copyright) 
        optional match (d)-[:PURCHASED_ASSET]-(a) 
        return 
            d.id as id,
            d.name as name,
            d.completed_date as completed_date,
            collect(distinct c.name) as rights_types, 
        ''' + self.add_base_params('d')
