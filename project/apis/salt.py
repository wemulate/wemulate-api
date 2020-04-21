from pepper import Pepper


class SaltApi(object):
    def __init__(self, url, user, sharedsecret):
        self.api = Pepper(url)
        self.api.login(user, sharedsecret, 'sharedsecret')

    def get_interfaces(self, device_name):
        return self.api.low([{'client': 'local', 'tgt': device_name, 'fun': 'wemulate.get_interfaces'}])

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
