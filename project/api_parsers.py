class ConnectionParser:

    def __init__(self, flaskApi):
        self.parser = flaskApi.parser()
        self.parser.add_argument(
            'connections',
            type=list,
            location='json'
        )

    def parse_arguments(self):
        args = self.parser.parse_args()
        return args['connections']


class DeviceParser:

    def __init__(self, flaskApi):
        self.parser = flaskApi.parser()
        self.parser.add_argument(
            'device_name',
            type=str,
            help='hostname of the device/minion'
        )
        self.parser.add_argument(
            'management_ip',
            type=str,
            help='define the management ip address (if not 127.0.0.1) of the device '
        )

    def parse_arguments(self):
        args = self.parser.parse_args()
        return args['device_name']
