from pepper import Pepper


class SaltApi(object):
    def __init__(self, url, user, sharedsecret):
        self.api = Pepper(url)
        self.api.login(user, sharedsecret, 'sharedsecret')

    def set_delay(self, name, delay):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.set_delay', 'arg': [name, delay]}])

    def remove_delay(self, name):
        return self.api.low([{'client': 'local', 'tgt': '*', 'fun': 'wemulate.remove_delay', 'arg': name}])
