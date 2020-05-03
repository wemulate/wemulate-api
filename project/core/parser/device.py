class DeviceParser:

    def __init__ (self, flaskApi):
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
        device_name = args['device_name']
        management_ip = args['management_ip']
        return device_name, management_ip
