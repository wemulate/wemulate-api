from types import SimpleNamespace


class ObjectMockup(SimpleNamespace):

    def __init__(self, serialize_map, **kwargs):
        SimpleNamespace.__init__(self, **kwargs)
        self.map = serialize_map

    def serialize(self):
        return {value: self.__dict__[key] for key, value in self.map.items() if key in self.__dict__}

class ConnectionMockup(ObjectMockup):

    def __init__(self, **kwargs):
        ObjectMockup.__init__(self, {
            'connection_name': 'connection_name',
            'first_logical_interface': 'interface1',
            'second_logical_interface': 'interface2',
            'corruption': 'corruption',
            'delay': 'delay',
            'duplication': 'duplication',
            'packet_loss': 'packet_loss',
            'bandwidth': 'bandwidth',
            'jitter': 'jitter',
        }, **kwargs)
