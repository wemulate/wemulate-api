from mockup.salt_mockup import SaltMockup
from apis.salt import SaltApi
import asyncio


class SaltInterface:

    def __init__(self):
        self.salt_api = None

    def init(self, app, url, user, sharedsecret):
        if app.config['SALT_MOCKUP']:
            self.salt_api = SaltMockup('url', 'salt', 'password')
        else:
            self.salt_api = SaltApi(url, user, sharedsecret)

    def __check_init(self):
        if self.salt_api is None:
            raise Exception(500, 'SaltInterface not initialized')

    def ready(self):
        self.__check_init()
        return self.salt_api.ready()

    def await_ready(self):
        self.__check_init()
        self.salt_api.await_ready()

    def get_interfaces(self, device_name):
        self.__check_init()
        return self.salt_api.get_interfaces(device_name)

    def get_management_ip(self, device_name):
        self.__check_init()
        return self.salt_api.get_management_ip(device_name)

    def add_connection(self, device_name, connection_name, interface1_name, interface2_name):
        self.__check_init()
        return self.salt_api.add_connection(device_name, connection_name, interface1_name, interface2_name)

    def remove_connection(self, device_name, connection_name):
        self.__check_init()
        return self.salt_api.remove_connection(device_name, connection_name)

    def set_parameters(self, device_name, interface_name, parameters):
        self.__check_init()
        return self.salt_api.set_parameters(device_name, interface_name, parameters)

    def remove_parameters(self, device_name, interface_name):
        self.__check_init()
        return self.salt_api.remove_parameters(device_name, interface_name)

    def update_connection(self, device_name, connection_name, interface1_name, interface2_name):
        self.__check_init()
        return self.salt_api.update_connection(device_name, connection_name, interface1_name, interface2_name)

    def update_parameters(self, device_name, interface_name, parameters):
        self.__check_init()
        return self.salt_api.update_parameters(device_name, interface_name, parameters)
