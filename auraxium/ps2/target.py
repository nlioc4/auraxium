from ..census import Query
from ..datatypes import StaticDatatype


class TargetType(StaticDatatype):
    _collection = 'target_type'

    def __init__(self, id):
        self.id = id
        data = super(TargetType, self).get_data(self)
        self.description = data['description']
