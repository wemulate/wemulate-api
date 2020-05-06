from pepper import Pepper
import time

# Default Interface Parameters
DEFAULT_PARAMETERS = {
    'bandwidth': 1000,
    'delay': 0,
    'jitter': 0,
    'packet_loss': 0,
    'corruption': 0,
    'duplication': 0
}
MAX_RETRIES = 6

class SaltApi(object):
    def __init__(self, url, user, sharedsecret):
        self.api = Pepper(url)
        retry_counter = 0
        while(retry_counter < MAX_RETRIES or SaltApi is None):
            retry_counter += 1
            try:
                self.api.login(user, sharedsecret, 'sharedsecret')
            except Exception as e:
                print(f"retry_counter {retry_counter}")
                if retry_counter < MAX_RETRIES:
                    time.sleep(10)
                else:
                    raise e

    def get_interfaces(self, device_name):
        return self.api.low([{'client': 'local', 'tgt': device_name, 'fun': 'wemulate.get_interfaces'}])

    def get_management_ip(self, device_name):
        return self.api.low([{'client': 'local', 'tgt': device_name, 'fun': 'wemulate.get_management_ip'}])

    def add_connection(self, device_name, connection_name, interface1_name, interface2_name):
        return self.api.low(
            [{'client': 'local', 'tgt': device_name, 'fun': 'wemulate.add_connection', 'arg': [
                connection_name, interface1_name, interface2_name]}])

    def remove_connection(self, device_name, connection_name):
        return self.api.low([
            {'client': 'local', 'tgt': device_name, 'fun': 'wemulate.remove_connection', 'arg': [connection_name]}])

    def set_parameters(self, device_name, interface_name, parameters):
        return self.api.low(
            [{'client': 'local',
              'tgt': device_name,
              'fun': 'wemulate.set_parameters',
              'arg': [interface_name, parameters]}]
        )

    def remove_parameters(self, device_name, interface_name):
        return self.api.low(
            [{'client': 'local',
              'tgt': device_name,
              'fun': 'wemulate.remove_parameters',
              'arg': [interface_name]}]
        )

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
            self.set_parameters(device_name, interface_name, parameters_to_apply)
