from app.models._query_manager import AbstractQueryManager


class TracksQueryManager(AbstractQueryManager):

    def __init__(self):
        super().__init__(alias='trk', label='Track', _id='TRK')

    _create = '''
    
        optional match (t:Track {name: $params.name})-[existingRel:RECORDED_BY]-(existingArtist:Artist {id:$params.artist_id})
        call (*) {
            match (t)
            where t is not null 
            return t as trk
            union 
            merge (newTrack:Track {name: $params.name})
            return newTrack as trk
        } 
        
    '''

    _search = '''
    where
        (tolower(trk.name) contains tolower($params.track_name) or $params.track_name is null) 
    with trk
    match (trk)-[:RECORDED_BY]-(artist)
    where tolower(artist.name) contains tolower($params.artist_name) or $params.artist_name is null
    '''  # Add link to tracks

    _with_relations = '''
    with trk
    optional match (trk)-[existingRel:RECORDED_BY]-(artist)
    where artist.id <> $params.artist_id
    
    call (*) { 
        with * 
        match (newArtist: Artist {id: $params.artist_id})
        foreach( _ in case when trk is not null then [1] else [] end |
        delete existingRel
        merge (trk)-[:RECORDED_BY]-(newArtist) 
        )
    }
    with trk
    '''

    def _return(self):
        return '''
        with trk
        
        match (trk)-[:RECORDED_BY]-(artist)
        
        return trk.id as id, 
                trk.name as name, 
                artist.name as artist_name, 
                artist.id as artist_id,
        ''' + self.add_base_params(self.alias)
