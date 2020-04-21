from pepper import Pepper


class SaltApi(object):
    def __init__(self, url, user, sharedsecret):
        self.api = Pepper(url)
        self.api.login(user, sharedsecret, 'sharedsecret')

    def get_interfaces(self):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.get_interfaces'}])

    def add_connection(self, connection_name, interface1_name, interface2_name):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.add_connection', 'arg': [connection_name, interface1_name, interface2_name]}])

    def remove_connection(self, connection_name):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.add_connection', 'arg': [connection_name]}])

    def set_parameters(self, interface_name, parameters):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.set_parameters', 'arg': [interface_name, parameters]}])

    def remove_parameters(self, interface_name):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.remove_parameters', 'arg': [interface_name]}])