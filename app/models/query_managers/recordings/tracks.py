from app.models._query_manager import AbstractQueryManager


class TracksQueryManager(AbstractQueryManager):

    def __init__(self):
        super().__init__(alias='trk', label='Track', _id='TRK')

    _create = '''
    '''

    _search = ''  # Add link to tracks
    _with_relations = ''

    def _return(self):
        return '''
        with trk
        
        match (trk)-[:RECORDED_BY]-(artist)
        
        return trk.id as id, 
                trk.name as name, 
                artist.name as artist_name, 
                artist.id as artist_id,
        ''' + self.add_base_params(self.alias)
