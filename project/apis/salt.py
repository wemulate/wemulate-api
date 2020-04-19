from pepper import Pepper


class SaltApi(object):
    def __init__(self, url, user, sharedsecret):
        self.api = Pepper(url)
        self.api.login(user, sharedsecret, 'sharedsecret')

    def set_delay(self, name, delay):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.set_delay', 'arg': [name, delay]}])

    def remove_delay(self, name):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.remove_delay', 'arg': name}])

    def get_interfaces(self):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.get_interfaces'}])

    def add_connection(self, connection_name, interface1_name, interface2_name):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.add_connection', 'arg': [connection_name, interface1_name, interface2_name]}])

    def remove_connection(self, connection_name, interface1_name, interface2_name):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.add_connection', 'arg': [connection_name, interface1_name, interface2_name]}])
