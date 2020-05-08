from core.database import db
from exception import WemulateException
import core.database.utils as dbutils

# Default Interface Parameters
DEFAULT_PARAMETERS = {
    'bandwidth': 1000,
    'delay': 0,
    'jitter': 0,
    'packet_loss': 0,
    'corruption': 0,
    'duplication': 0
}

DEVICES = {
    'wemulate_host1': {
        'interfaces': ['enp0s31f6', 'eth0', 'eth1', 'eth2', 'eth3', 'eth4'],
        'management_ip': '127.0.0.1'
    }
}

class SaltMockup:

    def __init__(self, url, user, sharedsecret):
        print('SaltMockup: Using SaltMockup')
        if len(dbutils.get_device_list()) == 0:
            for device_name, device in DEVICES.items():
                try:
                    profile = dbutils.create_profile(device_name)
                    db_device = dbutils.create_device(device_name, profile.profile_id, device['management_ip'])
                    interface_id = 1
                    for physical_name in device['interfaces']:
                        logical_interface = dbutils.get_logical_interface(interface_id)
                        dbutils.create_interface(physical_name, db_device.device_id,
                                                 logical_interface.logical_interface_id)
                        interface_id += 1
                except Exception as e:
                    raise WemulateException(500, f'SaltMockup: Error when creating device {device_name}: {str(e.args)}')
            db.session.commit()

    def read(self):
        return True

    def await_ready(self):
        # No implementation needed in mockup
        pass

    def get_interfaces(self, device_name):
        device = DEVICES[device_name]
        return {'return': [{device_name: device['interfaces']}]}

    def get_management_ip(self, device_name):
        device = DEVICES[device_name]
        return {'return': [{device_name: device['management_ip']}]}

    def add_connection(self, device_name, connection_name, interface1_name, interface2_name):
        # No implementation needed in mockup
        pass

    def remove_connection(self, device_name, connection_name):
        # No implementation needed in mockup
        pass

    def set_parameters(self, device_name, interface_name, parameters):
        # No implementation needed in mockup
        pass

    def remove_parameters(self, device_name, interface_name):
        # No implementation needed in mockup
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
