from types import SimpleNamespace


class SerializableMockup(SimpleNamespace):

    def __init__(self, serialize_map, **kwargs):
        SimpleNamespace.__init__(self, **kwargs)
        self.map = serialize_map

    def serialize(self):
        return {value: self.__dict__[key] for key, value in self.map.items()
                if key in self.__dict__ and not self.__dict__[key] is None}

class ConnectionMockup(SerializableMockup):

    def __init__(self, **kwargs):
        SerializableMockup.__init__(self, {
            'connection_name': 'connection_name',
            'interface1': 'interface1',
            'interface2': 'interface2',
            'corruption': 'corruption',
            'delay': 'delay',
            'duplication': 'duplication',
            'packet_loss': 'packet_loss',
            'bandwidth': 'bandwidth',
            'jitter': 'jitter',
        }, **kwargs)

class DeviceMockup(SerializableMockup):

    def __init__(self, **kwargs):
        SerializableMockup.__init__(self, {
            'device_id': 'device_id',
            'device_name': 'device_name',
            'management_ip': 'management_ip',
            'active_profile_name': 'active_profile_name'
        }, **kwargs)

class InterfaceMockup(SerializableMockup):

    def __init__(self, **kwargs):
        SerializableMockup.__init__(self, {
            'interface_id': 'interface_id',
            'physical_name': 'physical_name',
            'logical_name': 'logical_name'
        }, **kwargs)

class LogicalInterfaceMockup(SerializableMockup):

    def __init__(self, **kwargs):
        SerializableMockup.__init__(self, {
            'logical_interface_id': 'logical_interface_id',
            'logical_name': 'logical_name'
        }, **kwargs)
