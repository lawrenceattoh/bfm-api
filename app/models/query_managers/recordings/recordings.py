from app.models._query_manager import AbstractQueryManager


class RecordingsQueryManager(AbstractQueryManager):

    def __init__(self):
        super().__init__(alias='rec', label='Recording', _id='REC')

    _create = '''
    with trim(case when $params.isrc is null 
        then 'value' 
        else $params.isrc 
        end) as isrc
    merge (rec:Recording {isrc: isrc}) 
    '''

    _search = ''  # Add link to tracks
    _with_relations = ''

    def _return(self):
        return '''
        with *
        match (rec)-[:VERSION_OF]-(t:Track)
        
        return 
        rec.id as id,
        rec.isrc as isrc, 
        t.name as track_name,
        
        ''' + self.add_base_params(self.alias)
