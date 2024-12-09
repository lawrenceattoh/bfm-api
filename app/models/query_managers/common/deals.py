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
            
        match (d)-[:PARENT_CO]-(be:BusinessEntity)
        where (be.id = $params.business_entity_id OR $params.business_entity_id is null)
        
        with * 
        call (*) {
            with d
            optional match path = (d)-[:PURCHASED_ASSET]-(wrk:Work)-[:ROYALTY_SHARE]-(IpChain)-[:WRITER_SHARE]-(wri:Writer)
            where wri.id = $params.writer_id or $params.writer_id is null
            return count(path)> 0 as hasMatchingWriter
        }
        with d, be 
        where $params.writer_id is null or hasMatchingWriter
        '''

    @property
    def _with_relations(self) -> str:
        return '''
        with * 
            call (*) {
                with d, $params.business_entity_id as business_entity_id 
                where business_entity_id is not null 
                optional match (d)-[existingParentCo:PARENT_CO]-(existingBE:BusinessEntity)
                with d, existingBE, business_entity_id, existingParentCo
                match (newBE:BusinessEntity {id: business_entity_id})
                foreach (_ in case when business_entity_id = existingBE.id then [] else [1] end |
                delete (existingParentCo)
                merge (d)<-[:PARENT_CO]-(newBE)
                )
                return coalesce(newBE, existingBE) as be
            }
        '''

    def _return(self) -> str:
        return '''
        return 
            d.id as id,
            d.name as name,
            d.completed_date as completed_date,
            be.id as business_entity_id,
        ''' + self.add_base_params('d')
