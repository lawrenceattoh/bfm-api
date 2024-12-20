from app.models._query_manager import AbstractQueryManager


class ArtistQueryManager(AbstractQueryManager):

    def __init__(self):
        super().__init__(alias='art', label='Artist', _id='ART')

    _create = '''
    merge (art:Artist {name: $params.name}) 
    '''

    _search = '''
    where 
    (tolower(art.name) contains tolower($params.artist_name) or $params.artist_name is null) or 
    (art.id = $params.artist_id or $params.artist_id is null)
    
//    with art
  //  optional match (art)-[:
    
    '''

    def _return(self):
        return '''
    return 
        art.id as id, 
        art.name as name ,
    ''' + self.add_base_params('art')
