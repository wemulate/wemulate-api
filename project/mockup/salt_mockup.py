import core.service as wemulate_service

# Default Interface Parameters
DEFAULT_PARAMETERS = {
    'bandwidth': 1000,
    'delay': 0,
    'jitter': 0,
    'packet_loss': 0,
    'corruption': 0,
    'duplication': 0
}

DEVICES = [
    {
        'name': 'wemulate_host1',
        'interfaces': ['enp0s31f6', 'eth0', 'eth1']
    }
]

class SaltMockup:

    def __init__(self, url, user, sharedsecret):
        for device in DEVICES:
            try:
                wemulate_service.create_device(device['name'])
            except Exception as e:
                if e.args[0] == 400:
                    print(f'SaltMockup: Device {device['name']} already exists')
                else:
                    raise Exception(f'SaltMockup: Error when creating device {device['name']}: {str(e.args)}')

    def get_interfaces(self, device_name):
        return {'return': [{device['name']: device['interfaces']} for device in DEVICES]}

    def add_connection(self, device_name, connection_name, interface1_name, interface2_name):
        pass

    def remove_connection(self, device_name, connection_name):
        pass

    def set_parameters(self, device_name, interface_name, parameters):
        pass

    def remove_parameters(self, device_name, interface_name):
        pass

    def update_connection(self, device_name, connection_name, interface1_name, interface2_name):
        self.remove_connection(device_name, connection_name)
        self.add_connection(device_name, connection_name, interface1_name, interface2_name)

    def update_parameters(self, device_name, interface_name, parameters):
        parameters_to_apply = {}
        self.remove_parameters(device_name, interface_name)
        for name, value in parameters.items():
            if value != DEFAULT_PARAMETERS[name]:
                parameters_to_apply[name] = value
        if parameters_to_apply != {}:
            self.set_parameters(device_name, interface_name, parameters)
