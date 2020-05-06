from pepper import Pepper
import time
import asyncio

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
        self.loginTask = asyncio.create_task(self.__login(user, sharedsecret))

    async def __login(self, user, sharedsecret):
        retries = 0
        while True:
            try:
                self.api.login(user, sharedsecret, 'sharedsecret')
                break
            except Exception as e:
                retries += 1
                print(f"SaltApi: Login failed {retries}/{MAX_RETRIES} times")
                if retries < MAX_RETRIES:
                    await asyncio.sleep(10)
                else:
                    raise Exception(500, f'SaltApi: Error during login to salt: {str(e.args)}')

    def __check_ready(self):
        if self.ready():
            return
        else:
            raise Exception(500, f'SaltApi: Not ready')

    def ready(self):
        return self.loginTask.done()

    async def await_ready(self):
        await asyncio.gather(self.loginTask)

    def get_interfaces(self, device_name):
        self.__check_ready()
        return self.api.low([{'client': 'local', 'tgt': device_name, 'fun': 'wemulate.get_interfaces'}])

    def get_management_ip(self, device_name):
        self.__check_ready()
        return self.api.low([{'client': 'local', 'tgt': device_name, 'fun': 'wemulate.get_management_ip'}])

    def add_connection(self, device_name, connection_name, interface1_name, interface2_name):
        self.__check_ready()
        return self.api.low(
            [{'client': 'local', 'tgt': device_name, 'fun': 'wemulate.add_connection', 'arg': [
                connection_name, interface1_name, interface2_name]}])

    def remove_connection(self, device_name, connection_name):
        self.__check_ready()
        return self.api.low([
            {'client': 'local', 'tgt': device_name, 'fun': 'wemulate.remove_connection', 'arg': [connection_name]}])

    def set_parameters(self, device_name, interface_name, parameters):
        self.__check_ready()
        return self.api.low(
            [{'client': 'local',
              'tgt': device_name,
              'fun': 'wemulate.set_parameters',
              'arg': [interface_name, parameters]}]
        )

    def remove_parameters(self, device_name, interface_name):
        self.__check_ready()
        return self.api.low(
            [{'client': 'local',
              'tgt': device_name,
              'fun': 'wemulate.remove_parameters',
              'arg': [interface_name]}]
        )

    def update_connection(self, device_name, connection_name, interface1_name, interface2_name):
        self.__check_ready()
        self.remove_connection(device_name, connection_name)
        self.add_connection(device_name, connection_name, interface1_name, interface2_name)

    def update_parameters(self, device_name, interface_name, parameters):
        self.__check_ready()
        parameters_to_apply = {}
        self.remove_parameters(device_name, interface_name)
        for name, value in parameters.items():
            if value != DEFAULT_PARAMETERS[name]:
                parameters_to_apply[name] = value
        if parameters_to_apply != {}:
            self.set_parameters(device_name, interface_name, parameters_to_apply)
