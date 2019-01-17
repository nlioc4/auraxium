from ..census import Query
from ..datatypes import EnumeratedDataType
from ..misc import LocalizedString


class World(EnumeratedDataType):
    """A world in PS2.

    World is the internal name for game servers. Connery and Cobalt are
    worlds.

    """

    _collection = 'world'

    def __init__(self, id):
        self.id = id

        # Set default values
        self.name = None

    @property
    def status(self):
        print('NYI')

    def _populate(self, data=None):
        d = data if data != None else super()._get_data(self.id)

        # Set attribute values
        self.name = LocalizedString(d['name'])
