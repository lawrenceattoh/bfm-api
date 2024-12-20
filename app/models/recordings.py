from app.models._base import AbstractNode
from app.models.query_managers.recordings.artists import ArtistQueryManager
from app.models.query_managers.recordings.recordings import RecordingsQueryManager
from app.models.query_managers.recordings.tracks import TracksQueryManager


class Artists(AbstractNode):
    return_params = ['name']
    order_key = 'name'


class Recordings(AbstractNode):
    return_params = ['isrc']
    order_key = 't.name'


class Tracks(AbstractNode):
    return_params = ['name']
    order_key = 'name'


ModelArtist = Artists(ArtistQueryManager())
ModelRecordings = Recordings(RecordingsQueryManager())
ModelTracks = Tracks(TracksQueryManager())
